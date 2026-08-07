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
UNSUB_RE = re.compile(r"(is this email not relevant to you|prefer fewer emails from me).*", re.I | re.S)


def redact(text, first, company):
    text = UNSUB_RE.sub("", text)
    body, _sig = split_signature(text)
    body = URL_RE.sub("[LINK]", body)
    body = EMAIL_RE.sub("[EMAIL]", body)
    if first and len(first) >= 2:
        body = re.sub(re.escape(first), "[NAME]", body, flags=re.I)
    if company and len(company) >= 3:
        body = re.sub(re.escape(company), "[COMPANY]", body, flags=re.I)
    return body.strip()


def main():
    rescore = "--rescore" in sys.argv

    roles = pd.read_csv(os.path.join(OUT, "sender_roles.csv"))
    ca = set(roles[roles["ca_class"].isin(["confirmed_ca", "fallback_ca"])]["sender_local"])
    P = pd.read_parquet(os.path.join(DATA, "pushes_G30.parquet"))
    S = P[(P["in_study"]) & (P["channel"] == "mailbox") & (P["exclusions"] == "")
          & (P["sender_local"].isin(ca))]
    types = pd.read_parquet(os.path.join(DATA, "type_labels.parquet"))
    tmap = dict(zip(types["email_id"], types["type"]))
    S = S[S["opener_id"].astype(str).map(tmap).isin(["cold_pitch", "event_invite"])]
    ids = set(S["opener_id"].astype(str))

    cj = pd.read_parquet(os.path.join(DATA, "opener_contact_join.parquet"))
    cmap = {str(r["email_id"]): (r.get("firstname") or "", r.get("company") or "")
            for _, r in cj.iterrows()}

    items = []
    with gzip.open(os.path.join(DATA, "bodies_openers.jsonl.gz"), "rt") as f:
        for line in f:
            r = json.loads(line)
            if r["id"] not in ids:
                continue
            p = r["properties"]
            text = p.get("hs_email_text") or ""
            if not text.strip() and p.get("hs_email_html"):
                text, _ = html_to_text(p["hs_email_html"])
            text = strip_quoted(text)
            first, comp = cmap.get(r["id"], ("", ""))
            subj = p.get("hs_email_subject") or ""
            subj = URL_RE.sub("[LINK]", subj)
            if first:
                subj = re.sub(re.escape(first), "[NAME]", subj, flags=re.I)
            if comp and len(comp) >= 3:
                subj = re.sub(re.escape(comp), "[COMPANY]", subj, flags=re.I)
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
