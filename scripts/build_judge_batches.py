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
from text_clean import (html_to_text, strip_quoted, split_signature,
                        split_signature_strict)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "output")

URL_RE = re.compile(r"(https?://|www\.)[^\s<>\)\]]+", re.I)
# §9.7: a bare domain typed as prose ("have a look at Encord.com") carries no scheme
# and no www, so URL_RE never saw it and 25 items shipped one. It is a URL in
# substance and the §5.4 internal-domain check treats it as a leak, so it is redacted
# rather than argued about — the alternative is waiving a pre-registered gate because
# clearing it is inconvenient, which is the move pre-registration exists to prevent.
BARE_DOMAIN_RE = re.compile(
    r"\b(encord|tryencord)\.(com|ai|io)\b|\bcord\.tech\b", re.I)
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-']+@[A-Za-z0-9.\-]+")
UNSUB_RE = re.compile(
    r"(is this email not relevant to you|prefer fewer emails from me|"
    r"this email and any files transmitted with it are confidential).*", re.I | re.S)
DATE_RE = re.compile(r"\b20\d\d[-/]\d\d[-/]\d\d\b")
# Bare years only. Month/day ("the dinner on Jan 23rd") is CONTENT the judge rates for
# why_now and ask_clarity, so it is deliberately left in place.
YEAR_RE = re.compile(r"\b20[12]\d\b")
PLACEHOLDER_RE = re.compile(r"\[(NAME|COMPANY|LINK|EMAIL|DATE|YEAR|SENDER)\]")
MIN_RATABLE_WORDS = 8


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


SENDER_VOCAB = None       # pruned: tokens substituted inside the text
FULL_NAME_VOCAB = set()   # unpruned: used ONLY to spot a signature line that is a name


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


# §9.7: the contact-join name is not enough on its own. 13.3% of built items still
# opened with a real recipient name — HubSpot holds no firstname for 2,209 contacts, and
# reps write the nickname ("Hi Ed") where the record says "Edward". The result was a
# corpus where 77% of emails greeted "[NAME]" and 13% greeted a warm-sounding real
# person, which is a difference a judge could read as bespokeness. This catches the
# residue by POSITION instead of by lookup.
GREETING_RE = re.compile(
    r"^([ \t]*(?:hi|hey|hello|dear|hiya|bonjour|salut|hallo|guten tag|ciao|hola|"
    r"good morning|good afternoon)\b[ \t]+)([A-Z][A-Za-z'\-]{1,20})", re.I | re.M)
GREETING_STOP = {"there", "all", "team", "folks", "everyone", "both", "guys", "again",
                 "and", "encord"}


def redact_greeting(text):
    def sub(m):
        if m.group(2).lower() in GREETING_STOP:
            return m.group(0)
        return m.group(1) + "[NAME]"
    return GREETING_RE.sub(sub, text)


def redact(text, first, company):
    text = UNSUB_RE.sub("", text)
    # §9.7: the STRICT splitter, judge path only. The counting splitter left a full
    # signature block on 29.8% of items, which told the judge who wrote the email.
    body, _sig = split_signature_strict(text, names=FULL_NAME_VOCAB)
    body = URL_RE.sub("[LINK]", body)
    # EMAIL_RE MUST run before BARE_DOMAIN_RE. Reversed, the domain half of
    # 'james.sweeney@encord.com' becomes '[LINK]', EMAIL_RE no longer matches, and the
    # local part — the sender's actual name — survives. Caught by test D9.
    body = EMAIL_RE.sub("[EMAIL]", body)
    body = BARE_DOMAIN_RE.sub("[LINK]", body)
    body = DATE_RE.sub("[DATE]", body)
    body = YEAR_RE.sub("[YEAR]", body)
    body = redact_names(body, first, company)
    body = redact_greeting(body)
    # residual sender identity (signature blocks that survived the split)
    for tok in SENDER_VOCAB:
        body = re.sub(rf"\b{re.escape(tok)}\b", "[SENDER]", body, flags=re.I)
    body = re.sub(r"(\[SENDER\][\s,|]*){2,}", "[SENDER] ", body)
    return body.strip()


def redact_subject(subj, first, company):
    """§9.7: the subject was previously given only URL + recipient-name redaction.

    It never had EMAIL_RE applied, so calendar-invite subjects shipped the sender's
    own address to the judge — '... 2:30pm - 3pm (GMT) (james.sweeney@encord.com)'.
    That also poisoned the lowercase test in prune_common_words. The subject now gets
    the same treatment as the body.
    """
    subj = URL_RE.sub("[LINK]", subj)
    subj = EMAIL_RE.sub("[EMAIL]", subj)      # order matters — see redact(), test D9
    subj = BARE_DOMAIN_RE.sub("[LINK]", subj)
    subj = DATE_RE.sub("[DATE]", subj)
    subj = YEAR_RE.sub("[YEAR]", subj)
    subj = redact_names(subj, first, company)
    for tok in SENDER_VOCAB:
        subj = re.sub(rf"\b{re.escape(tok)}\b", "[SENDER]", subj, flags=re.I)
    return subj.strip()


def ratable_words(text):
    """Real words left for a judge to rate, ignoring placeholders."""
    return len(re.findall(r"[A-Za-z]{2,}", PLACEHOLDER_RE.sub(" ", text)))


CALENDAR_WORDS = {
    "jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "sept", "oct",
    "nov", "dec", "mon", "tue", "tues", "wed", "thu", "thur", "thurs", "fri", "sat", "sun",
}


def prune_common_words(vocab, texts, min_items=3, min_share_of_uses=0.2):
    """Drop name tokens that are also ordinary English.

    Some reps share a surname with a common word (an owner surnamed "Short" turned
    "a short call" into "a [SENDER] call"), so a blanket redaction damages the text
    the judge must rate.

    RUN2_PREREGISTRATION §9.7 — the original rule pruned any token appearing in more
    than 2% of emails, on the theory that a frequent token must be vocabulary. That
    reasoning inverts exactly where it matters: a PROLIFIC REP'S NAME IS FREQUENT
    BECAUSE THEY ARE PROLIFIC. It pruned `decaudaveine`, `fourati`, `kirpalani`,
    `landau`, `hansen`, `ulrik` (13.2% of items) and `sweeney` — all unambiguous
    identity — and 29.8% of built judge items carried a sender name as a result. That
    is the run-1 leak rate (~30%) the §5.4 check exists to prevent, reproduced by the
    fix meant to prevent it.

    The replacement asks a question frequency cannot answer: DOES THIS TOKEN EVER
    APPEAR LOWERCASE? Ordinary words do, constantly ("a short call", "the team",
    "will be hosting"). Names do not — English capitalises them everywhere. A token
    is kept as identity unless it appears lowercase in at least `min_items` distinct
    emails AND lowercase uses are at least `min_share_of_uses` of its total uses, so a
    single typo cannot unblind a rep.

    `texts` MUST already have email addresses and URLs redacted: the lowercase test is
    otherwise contaminated by the sender's own address ('james.sweeney@encord.com'
    made `james`, `sweeney` and `skander` look like ordinary words).

    Month and weekday abbreviations are pruned unconditionally — they collide with
    real names (`jan`), are never identity in this corpus, and carry the why-now
    content the judge is asked to rate ("the dinner on Jan 23rd").
    """
    kept, dropped = set(), set()
    for v in vocab:
        if v in CALENDAR_WORDS:
            dropped.add(v)
            continue
        low_rx = re.compile(rf"(?<![A-Za-z]){re.escape(v)}\b")
        any_rx = re.compile(rf"\b{re.escape(v)}\b", re.I)
        n_low = sum(1 for t in texts if low_rx.search(t))
        n_any = sum(1 for t in texts if any_rx.search(t))
        if n_low >= min_items and n_any and n_low / n_any >= min_share_of_uses:
            dropped.add(v)
        else:
            kept.add(v)
    if dropped:
        print(f"  not redacted (ordinary words / calendar): {sorted(dropped)}")
    return sorted(kept, key=len, reverse=True)


def main():
    global SENDER_VOCAB, FULL_NAME_VOCAB
    rescore = "--rescore" in sys.argv

    # Corpus = the union of the G21/G30/G45 analysis frames (§9.7).
    #
    # Judging stays independent of the TYPE classifier — types are not consulted here,
    # so the two blind passes still do not depend on each other's completion, which was
    # the original reason for selecting straight from pushes_G30.
    #
    # What changed: selecting from pushes alone also swept in openers that no frame
    # contains — replies inside an existing thread ("Re: Techex Expo" -> "Assume you're
    # busy with the presentation?") and, in one case, a triathlon training plan. 3,183
    # of 15,173 built items (21%) could never enter any analysis, and would have been
    # paid for. In the other direction, 487 rows that ARE in a frame had no judge
    # coverage at all, which would have left the G21/G45 robustness runs with holes.
    #
    # Frame membership is decided by eligibility (bounce, gap, thread position, CA
    # sender, study window) and never by outcome, so this does not weaken blinding: the
    # judge still sees no outcome, no sender and no date.
    ids = set()
    for G in (21, 30, 45):
        fr = pd.read_parquet(os.path.join(DATA, f"frame_G{G}.parquet"),
                             columns=["email_id"])
        ids.update(fr["email_id"].astype(str))
    print(f"  corpus: union of G21/G30/G45 frames = {len(ids)} openers")

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

    FULL_NAME_VOCAB = build_sender_vocab()
    # §9.7: prune on the text AS THE JUDGE WILL SEE IT — signature removed, addresses
    # and URLs gone. Two earlier versions of this decision were made on the wrong text
    # and both let a name through:
    #   raw text, addresses intact -> 'james.sweeney@encord.com' made `james`,
    #     `sweeney`, `skander` look like ordinary lowercase words
    #   raw text, signature intact -> a lowercase handle inside a signature block that
    #     is later stripped made `zainab` look like one
    # The vocabulary must be decided on the same string the leak would appear in.
    scrub = [EMAIL_RE.sub(" ", URL_RE.sub(
        " ", (s or "") + " \n " + split_signature_strict(t, names=FULL_NAME_VOCAB)[0]))
        for _, s, t in raw]
    SENDER_VOCAB = prune_common_words(FULL_NAME_VOCAB, scrub)

    items, dropped_thin = [], 0
    if True:
        for r_id, subj_raw, text in raw:
            first, comp = cmap.get(r_id, ("", ""))
            subj = redact_subject(subj_raw, first, comp)
            body = redact(text, first, comp)
            if not body.strip():
                continue
            # nothing left to rate: an email that was only links, or a two-word note
            if ratable_words(body) < MIN_RATABLE_WORDS:
                dropped_thin += 1
                continue
            items.append({"id": r_id, "subject": subj[:150], "text": body[:2400]})

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
    print(f"  dropped, under {MIN_RATABLE_WORDS} ratable words after redaction: {dropped_thin}")


if __name__ == "__main__":
    main()
