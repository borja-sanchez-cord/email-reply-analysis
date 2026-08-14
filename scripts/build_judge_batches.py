"""Build blinded judge batches per rules/judge_rubric.md.

Corpus: clean mailbox openers in the study window from CA-class senders
(confirmed_ca + fallback_ca), types cold_pitch and event_invite.

Redaction (blinding): recipient first name -> [NAME]; recipient company -> [COMPANY];
URLs -> [LINK]; email addresses -> [EMAIL]; signature/footer removed; unsubscribe
footer removed. No sender, no date, no outcome anywhere in the batch files.

Usage: python3 build_judge_batches.py            (main pass, batches of 40)
       python3 build_judge_batches.py --rescore  (random 10%, seed-shifted batches)
"""
import gzip
import json
import os
import random
import re
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from text_clean import html_to_text, strip_quoted, split_signature

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "output")

URL_RE = re.compile(r"(https?://|www\.)[^\s<>\)\]]+", re.I)
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-']+@[A-Za-z0-9.\-]+")
UNSUB_RE = re.compile(
    r"(is this email not relevant to you|prefer fewer emails from me|"
    r"this email and any files transmitted with it are confidential).*", re.I | re.S)
DATE_RE = re.compile(r"\b20\d\d[-/]\d\d[-/]\d\d\b")


def build_sender_vocab():
    """Every token that could identify the SENDER — the judge must never see who
    wrote the email (rules/judge_rubric.md, rule 1). Built from the owner records
    (first/last names, email local parts) plus the sender locals seen in the data."""
    vocab = set()
    owners = json.load(open(os.path.join(DATA, "owners.json")))
    for o in owners:
        for k in ("firstName", "lastName"):
            v = (o.get(k) or "").strip()
            if len(v) >= 3:
                vocab.add(v.lower())
        em = (o.get("email") or "").lower()
        if em:
            for part in re.split(r"[._@]", em.split("@")[0]):
                if len(part) >= 3:
                    vocab.add(part)
    roles = pd.read_csv(os.path.join(OUT, "sender_roles.csv"))
    for local in roles["sender_local"]:
        for part in re.split(r"[._]", str(local)):
            if len(part) >= 3:
                vocab.add(part.lower())
    vocab.discard("encord")
    vocab.discard("cord")
    return vocab


SENDER_VOCAB = None


def redact_names(text, first, company):
    """Replace the recipient's name and company, WITH WORD BOUNDARIES.

    Run 2 fix (RUN2_PREREGISTRATION §5.4, over-redaction half). The original did a
    bare re.escape substitution with no boundaries, so a recipient named "Al" turned
    "also" into "[NAME]so" and a company called "Speak" turned "speaking" into
    "[COMPANY]ing" — the same defect that was already fixed on the feature path
    (features_compute.py, audit finding 5). Judges rate the text they are shown, so
    mangled words cost real signal on polish, economy and bespokeness.

    Boundaries only tighten the match, so this removes over-redaction without
    introducing under-redaction: "\\bAl\\b" still catches the actual name.
    Short single-word company names additionally require the capitalised form,
    mirroring the rule already audited on the feature path.
    """
    if first and len(first) >= 2:
        text = re.sub(rf"\b{re.escape(first)}\b", "[NAME]", text, flags=re.I)
    if company and len(company) >= 3:
        if " " not in company and len(company) <= 6:
            cased = company[0].upper() + company[1:]
            text = re.sub(rf"\b{re.escape(cased)}\b", "[COMPANY]", text)
        else:
            text = re.sub(rf"\b{re.escape(company)}\b", "[COMPANY]", text, flags=re.I)
    return text


def redact(text, first, company):
    text = UNSUB_RE.sub("", text)
    body, _sig = split_signature(text)
    body = URL_RE.sub("[LINK]", body)
    body = EMAIL_RE.sub("[EMAIL]", body)
    body = DATE_RE.sub("[DATE]", body)
    body = redact_names(body, first, company)
    # residual sender identity (signature blocks that survived the split)
    for tok in SENDER_VOCAB:
        body = re.sub(rf"\b{re.escape(tok)}\b", "[SENDER]", body, flags=re.I)
    body = re.sub(r"(\[SENDER\][\s,|]*){2,}", "[SENDER] ", body)
    return body.strip()


def prune_common_words(vocab, texts, max_share=0.02):
    """Drop name tokens that are also ordinary English.

    Some reps share a surname with a common word (an owner surnamed "Short" turned
    "a short call" into "a [SENDER] call"). Any token appearing in more than
    `max_share` of emails is treated as vocabulary, not identity, and left alone —
    measured from the corpus itself rather than a hand-written stoplist.
    """
    from collections import Counter
    c = Counter()
    for t in texts:
        for w in set(re.findall(r"[a-z]{3,}", t.lower())):
            c[w] += 1
    n = max(1, len(texts))
    kept = {v for v in vocab if c[v] / n <= max_share}
    dropped = sorted(vocab - kept)
    if dropped:
        print(f"  not redacted (too common to be identity): {dropped}")
    return sorted(kept, key=len, reverse=True)


def main():
    global SENDER_VOCAB
    rescore = "--rescore" in sys.argv

    # Judge every eligible CA opener, independent of the type classifier: judging and
    # typing are separate blind passes, and filtering to cold_pitch/event_invite at
    # analysis time keeps the two from depending on each other's completion.
    roles = pd.read_csv(os.path.join(OUT, "sender_roles.csv"))
    ca = set(roles[roles["ca_class"].isin(["confirmed_ca", "fallback_ca"])]["sender_local"])
    P = pd.read_parquet(os.path.join(DATA, "pushes_G30.parquet"))
    S = P[(P["in_study"]) & (P["channel"] == "mailbox") & (P["exclusions"] == "")
          & (P["sender_local"].isin(ca))]
    ids = set(S["opener_id"].astype(str))

    cj = pd.read_parquet(os.path.join(DATA, "opener_contact_join.parquet"))
    cmap = {str(r["email_id"]): (r.get("firstname") or "", r.get("company") or "")
            for _, r in cj.iterrows()}

    # pass 1: collect the raw bodies (needed to decide which name tokens are
    # actually ordinary English before anything is redacted)
    raw = []
    with gzip.open(os.path.join(DATA, "bodies_openers.jsonl.gz"), "rt") as f:
        for line in f:
            r = json.loads(line)
            if r["id"] not in ids:
                continue
            p = r["properties"]
            text = p.get("hs_email_text") or ""
            if not text.strip() and p.get("hs_email_html"):
                text, _ = html_to_text(p["hs_email_html"])
            raw.append((r["id"], p.get("hs_email_subject") or "", strip_quoted(text)))
    SENDER_VOCAB = prune_common_words(build_sender_vocab(), [t for _, _, t in raw])

    items = []
    if True:
        for r_id, subj_raw, text in raw:
            r = {"id": r_id}
            p = {"hs_email_subject": subj_raw}
            first, comp = cmap.get(r["id"], ("", ""))
            subj = subj_raw
            subj = URL_RE.sub("[LINK]", subj)
            subj = redact_names(subj, first, comp)
            for tok in SENDER_VOCAB:
                subj = re.sub(rf"\b{re.escape(tok)}\b", "[SENDER]", subj, flags=re.I)
            body = redact(text, first, comp)
            if not body.strip():
                continue
            items.append({"id": r["id"], "subject": subj[:150], "text": body[:2400]})

    items.sort(key=lambda x: x["id"])
    if rescore:
        random.Random(77).shuffle(items)
        items = items[: max(1, len(items) // 10)]
        out_dir = os.path.join(OUT, "judge_batches_rescore")
    else:
        out_dir = os.path.join(OUT, "judge_batches")
    os.makedirs(out_dir, exist_ok=True)
    B = 40
    n = 0
    for i in range(0, len(items), B):
        with open(os.path.join(out_dir, f"batch_{i // B:04d}.json"), "w") as f:
            json.dump(items[i:i + B], f, indent=0)
        n += 1
    print(f"{len(items)} openers -> {n} judge batches in {out_dir}")


if __name__ == "__main__":
    main()
