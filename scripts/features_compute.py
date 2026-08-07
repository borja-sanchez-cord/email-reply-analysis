"""Step 4a — computed features on opener bodies. Every counter gets audited
(scripts/audit_features.py prints 20 flagged examples per feature) before any
analysis uses it.

Usage: python3 features_compute.py <opener_bodies.jsonl.gz> <contacts_join.parquet> <out.parquet>

Features (floor list from the brief + additions):
  words, sentences, paragraphs, questions (real, in body-not-footer), first question length,
  links, bullets, bold, images, subject length/words, subject_is_question,
  greeting style, sign-off style, mentions of first name (in greeting / beyond greeting),
  mentions of company name, mentions of role words, template repeats (personalisation-
  stripped body hash), sent hour/day (descriptive), body starts with recipient first name.
"""
import gzip
import hashlib
import json
import os
import re
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from text_clean import html_to_text, strip_quoted, split_signature, unwrap, tidy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

UNSUB_TAIL = re.compile(
    r"(is this email not relevant to you|prefer fewer emails from me|"
    r"this email and any files transmitted with it are confidential).*",
    re.I | re.S)

URL_RE = re.compile(r"https?://[^\s<>\)\]]+", re.I)
SENT_SPLIT = re.compile(r"[.!?]+[\s\n]")
FOOTER_QUESTION_MARKERS = re.compile(
    r"(unsubscribe|not relevant to you|opt.?out|stop receiving|manage preferences)", re.I)
GREETING_RE = re.compile(
    r"^\s*(hi|hey|hello|dear|good (morning|afternoon|evening)|greetings|howdy)\b[\s,]*([A-Z][a-z]+)?",
    re.I)
ROLE_WORDS = re.compile(
    r"\b(your (role|team|work|research|pipeline|projects?|models?)|as (an?|the) "
    r"(head|lead|director|vp|manager|engineer|scientist|founder|cto|ceo|cpo))\b", re.I)


def clean_body(p):
    """Return (body_text, fmt) where body_text is the message body (quoted trail,
    signature and unsubscribe footer removed, hard wraps joined) and fmt counts
    formatting markup **inside the body only**.

    Formatting is measured on the HTML rendering with offset tracking: signature
    blocks carry logo <img> tags and bold contact lines, and counting those as
    body formatting inflated has_bold to 77% and n_images to 75% of all emails
    (audit finding, 2026-08-07).
    """
    html = p.get("hs_email_html") or ""
    fmt = {"n_images": 0, "n_bullets": 0, "bold_chars": 0, "has_html": bool(html)}

    if html:
        raw_html_text, meta = html_to_text(html)
        # locate the body region within raw_html_text (offsets valid there)
        cut_src = strip_quoted(raw_html_text)
        cut_src = UNSUB_TAIL.sub("", cut_src)
        body_part, _sig = split_signature(cut_src)
        # body_part is a prefix of raw_html_text up to whitespace normalisation;
        # use its length as the offset threshold (conservative: quoted-trail and
        # signature removal only ever shorten the prefix)
        limit = len(body_part)
        fmt["n_images"] = sum(1 for o in meta.get("images", []) if o < limit)
        fmt["n_bullets"] = sum(1 for o in meta.get("bullets", []) if o < limit)
        fmt["bold_chars"] = sum(n for o, n in meta.get("bold_runs", []) if o < limit)

    text = p.get("hs_email_text") or ""
    if not text.strip() and html:
        text = html_to_text(html)[0]
    return strip_quoted(tidy(text)), fmt


def norm_name(s):
    return (s or "").strip().lower()


def personalisation_stripped_hash(body, first, company):
    t = body.lower()
    if first:
        t = t.replace(first.lower(), " ")
    if company:
        t = t.replace(company.lower(), " ")
    t = URL_RE.sub(" ", t)
    t = re.sub(r"[a-z0-9._%+\-']+@[a-z0-9.\-]+", " ", t)
    t = re.sub(r"\d+", " ", t)
    t = re.sub(r"[^a-z ]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return hashlib.md5(t.encode()).hexdigest(), len(t)




def featurize(rec, contact):
    p = rec["properties"]
    subject = p.get("hs_email_subject") or ""
    raw_body, meta = clean_body(p)
    raw_body = UNSUB_TAIL.sub("", raw_body)  # audit finding: footers survive signature split
    body, signature = split_signature(raw_body)
    # audit finding: hard-wrapped plaintext made lines look like sentences and
    # truncated questions at the wrap point — unwrap before any text measurement
    body = unwrap(body)

    first = norm_name(contact.get("firstname"))
    company = norm_name(contact.get("company") or contact.get("organisation_name"))
    # audit findings: 2-letter names ("Or") match prose; short common-word companies
    # ("Speak") match verbs. Names need >=3 chars + word boundaries; single short
    # company words require the capitalised form in the original text.
    if len(first) < 3:
        first = ""
    if len(company) < 3:
        company = ""
    company_needs_case = bool(company) and (" " not in company) and len(company) <= 6

    # n_links BEFORE removing urls (body has signature stripped already)
    n_links = len(URL_RE.findall(body))
    # all word/sentence/question features are computed with URLs collapsed to a
    # single token — otherwise long tracking URLs inflate word counts and their
    # '?' query strings get counted as questions (audit finding, 2026-08-07)
    body_t = URL_RE.sub("[LINK]", body)

    words = re.findall(r"[A-Za-z0-9''\-\[\]]+", body_t)
    # paragraphs: blank-line-separated blocks with >=4 words (skips stray single-line
    # artefacts from html rendering)
    paragraphs = [x for x in re.split(r"\n\s*\n", body_t)
                  if len(x.split()) >= 4]
    # sentences: split on ./!/? followed by space-or-newline OR on newlines that end
    # a >=4-word line (emails often use bare linebreaks as sentence ends)
    sent_chunks = re.split(r"(?:[.!?]+\s+|\n+)", body_t)
    sentences = [s for s in sent_chunks if len(s.split()) >= 3]

    # real questions: question sentences (URLs already collapsed; signature stripped;
    # body unwrapped so a question is never cut at a line wrap),
    # not matching unsubscribe-footer phrasing
    q_sents = [s.strip() for s in re.split(r"(?<=[.!?])\s|\n", body_t)
               if s.strip().endswith("?")]
    q_sents = [q for q in q_sents if not FOOTER_QUESTION_MARKERS.search(q)
               and len(q.replace("[LINK]", "").strip()) > 2]
    first_q = q_sents[0] if q_sents else ""

    g = GREETING_RE.match(body)
    greeting_style = g.group(1).lower() if g else ("name_only" if first and
                     body.lower().startswith(first) else "none")
    # greeting zone = the whole first line (multi-name greetings: "Hi A, B and C,")
    first_nl = body.find("\n")
    greeting_zone = body[:first_nl if first_nl > 0 else len(body)].lower()
    greeting_has_name = bool(first and g and
                             re.search(rf"\b{re.escape(first)}\b", greeting_zone))

    body_after_greeting = body[len(greeting_zone):]
    bl = body.lower()


    h, tlen = personalisation_stripped_hash(body, first, company)

    return {
        "email_id": rec["id"],
        "n_words": len(words),
        "n_sentences": len(sentences),
        "n_paragraphs": len(paragraphs),
        "n_questions": len(q_sents),
        "first_question_words": len(first_q.split()) if first_q else 0,
        "n_links": n_links,
        # max, not sum: when the body text came from the HTML rendering the "• "
        # markers are the same <li> elements the markup counter already saw
        "n_bullets": max(meta.get("n_bullets", 0),
                         len(re.findall(r"^\s*[•\-\*]\s+\S", body, re.M))),
        "has_bold": meta.get("bold_chars", 0) > 0,
        "n_images": meta.get("n_images", 0),
        "has_html": meta.get("has_html", False),
        "subject_chars": len(subject),
        "subject_words": len(subject.split()),
        "subject_is_question": subject.strip().endswith("?"),
        "subject_has_name": bool(first and re.search(rf"\b{re.escape(first)}\b",
                                                     subject.lower())),
        "subject_has_company": bool(company and (
            re.search(re.escape(company[0].upper() + company[1:]), subject)
            if company_needs_case
            else re.search(rf"\b{re.escape(company)}\b", subject.lower()))),
        "greeting_style": greeting_style,
        "greeting_has_name": greeting_has_name,
        "name_beyond_greeting": bool(first and re.search(
            rf"\b{re.escape(first)}\b", body_after_greeting.lower())),
        "mentions_company": bool(company and (
            re.search(re.escape(company[0].upper() + company[1:]), body)
            if company_needs_case
            else re.search(rf"\b{re.escape(company)}\b", bl))),
        "mentions_role_words": bool(ROLE_WORDS.search(body)),
        "has_signature_block": bool(signature),
        "template_hash": h,
        "template_hash_len": tlen,
        "body_chars": len(body),
        "empty_body": len(body.strip()) == 0,
    }


def main():
    bodies_path, contacts_path, out_path = sys.argv[1:4]
    contact_by_email_id = {}
    cj = pd.read_parquet(contacts_path)  # email_id -> contact fields
    for _, r in cj.iterrows():
        contact_by_email_id[str(r["email_id"])] = r.to_dict()

    rows = []
    with gzip.open(os.path.join(DATA, bodies_path), "rt") as f:
        for line in f:
            rec = json.loads(line)
            rows.append(featurize(rec, contact_by_email_id.get(str(rec["id"]), {})))
    df = pd.DataFrame(rows)

    # template repeats: count within this corpus (segment equalisation happens at
    # analysis time per trap 5; the raw count is stored here)
    counts = df.groupby("template_hash")["email_id"].transform("count")
    df["template_repeats"] = counts
    df["is_template_3plus"] = (counts >= 3) & (df["template_hash_len"] >= 40)

    df.to_parquet(os.path.join(DATA, out_path), index=False)
    print(f"wrote {len(df)} feature rows -> {out_path}")
    print(df.drop(columns=["email_id", "template_hash"]).describe(include="all").to_string())


if __name__ == "__main__":
    main()
