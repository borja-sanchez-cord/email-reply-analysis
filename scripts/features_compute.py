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
from text_clean import html_to_text, strip_quoted, split_signature

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

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
    text = p.get("hs_email_text") or ""
    meta = {}
    if not text.strip() and p.get("hs_email_html"):
        text, meta = html_to_text(p["hs_email_html"])
    else:
        # links/format signals from html when available even if text exists
        if p.get("hs_email_html"):
            _, meta = html_to_text(p["hs_email_html"])
    return strip_quoted(text), meta


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
    body, signature = split_signature(raw_body)

    first = norm_name(contact.get("firstname"))
    company = norm_name(contact.get("company") or contact.get("organisation_name"))
    if len(first) < 2:
        first = ""
    if len(company) < 3:
        company = ""

    words = re.findall(r"[A-Za-z0-9''\-]+", body)
    paragraphs = [x for x in re.split(r"\n\s*\n", body) if x.strip()]
    sentences = [s for s in SENT_SPLIT.split(body) if s.strip()]

    # real questions: '?' sentences in body (signature/footer excluded by split),
    # not matching unsubscribe-footer phrasing
    q_sents = [s.strip() for s in re.split(r"(?<=\?)", body) if s.strip().endswith("?")]
    q_sents = [q for q in q_sents if not FOOTER_QUESTION_MARKERS.search(q)]
    first_q = q_sents[0] if q_sents else ""

    g = GREETING_RE.match(body)
    greeting_style = g.group(1).lower() if g else ("name_only" if first and
                     body.lower().startswith(first) else "none")
    greeting_has_name = bool(first and g and first in (g.group(0) or "").lower())

    body_after_greeting = body[g.end():] if g else body
    bl = body.lower()

    links = URL_RE.findall(body)
    n_links = max(len(links), len(meta.get("links", [])))

    h, tlen = personalisation_stripped_hash(body, first, company)

    return {
        "email_id": rec["id"],
        "n_words": len(words),
        "n_sentences": len(sentences),
        "n_paragraphs": len(paragraphs),
        "n_questions": len(q_sents),
        "first_question_words": len(first_q.split()) if first_q else 0,
        "n_links": n_links,
        "n_bullets": meta.get("n_bullets", 0) + len(re.findall(r"^\s*[•\-\*]\s+\S", body, re.M)),
        "has_bold": meta.get("bold_chars", 0) > 0,
        "n_images": meta.get("n_images", 0),
        "subject_chars": len(subject),
        "subject_words": len(subject.split()),
        "subject_is_question": subject.strip().endswith("?"),
        "subject_has_name": bool(first and first in subject.lower()),
        "subject_has_company": bool(company and company in subject.lower()),
        "greeting_style": greeting_style,
        "greeting_has_name": greeting_has_name,
        "name_beyond_greeting": bool(first and first in body_after_greeting.lower()),
        "mentions_company": bool(company and company in bl),
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
