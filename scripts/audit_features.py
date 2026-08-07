"""Audit every counter: print 20 random flagged examples per feature with the
relevant text so a reader can verify the counter counts what it claims.
(Trap: last study's question-counter was counting the unsubscribe footer.)

Usage: python3 audit_features.py [feature ...]   (default: the risky ones)
"""
import gzip
import json
import os
import random
import re
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from text_clean import html_to_text, strip_quoted, split_signature, unwrap
from features_compute import (clean_body, FOOTER_QUESTION_MARKERS, GREETING_RE,
                              ROLE_WORDS, URL_RE, UNSUB_TAIL)


def audit_body(p):
    """Reproduce EXACTLY the text features_compute.py measures, so the audit
    shows what the counter actually sees (not an approximation of it)."""
    raw, meta = clean_body(p)
    raw = UNSUB_TAIL.sub("", raw)
    body, _sig = split_signature(raw)
    body = unwrap(body)
    return body, URL_RE.sub("[LINK]", body), meta


def audit_questions(body_t):
    qs = [s.strip() for s in re.split(r"(?<=[.!?])\s|\n", body_t)
          if s.strip().endswith("?")]
    return [q for q in qs if not FOOTER_QUESTION_MARKERS.search(q)
            and len(q.replace("[LINK]", "").strip()) > 2]

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")


def load_bodies(ids):
    out = {}
    with gzip.open(os.path.join(DATA, "bodies_openers.jsonl.gz"), "rt") as f:
        for line in f:
            r = json.loads(line)
            if r["id"] in ids:
                out[r["id"]] = r["properties"]
    return out


CHECKS = {
    "n_questions": ("n_questions >= 1", lambda F: F["n_questions"] >= 1),
    "no_questions": ("n_questions == 0", lambda F: F["n_questions"] == 0),
    "n_bullets": ("n_bullets >= 1", lambda F: F["n_bullets"] >= 1),
    "has_bold": ("has_bold", lambda F: F["has_bold"]),
    "n_images": ("n_images >= 1", lambda F: F["n_images"] >= 1),
    "n_links": ("n_links >= 1", lambda F: F["n_links"] >= 1),
    "subject_is_question": ("subject_is_question", lambda F: F["subject_is_question"]),
    "greeting_none": ("greeting_style == none", lambda F: F["greeting_style"] == "none"),
    "name_beyond_greeting": ("name_beyond_greeting", lambda F: F["name_beyond_greeting"]),
    "mentions_company": ("mentions_company", lambda F: F["mentions_company"]),
    "mentions_role_words": ("mentions_role_words", lambda F: F["mentions_role_words"]),
    "is_template_3plus": ("is_template_3plus", lambda F: F["is_template_3plus"]),
    "not_template": ("template_repeats == 1", lambda F: F["template_repeats"] == 1),
    "short": ("n_words <= 60", lambda F: F["n_words"] <= 60),
}


def main():
    feats = pd.read_parquet(os.path.join(DATA, "features_openers.parquet"))
    cj = pd.read_parquet(os.path.join(DATA, "opener_contact_join.parquet"))
    cmap = {str(r["email_id"]): r.to_dict() for _, r in cj.iterrows()}
    which = sys.argv[1:] or list(CHECKS)
    for name in which:
        label, pred = CHECKS[name]
        sub = feats[feats.apply(pred, axis=1)]
        n = min(20, len(sub))
        sample = sub.sample(n, random_state=13)
        bodies = load_bodies(set(sample["email_id"]))
        print("\n" + "#" * 90)
        print(f"### AUDIT {name} ({label}) — {len(sub)} flagged, showing {n}")
        for _, row in sample.iterrows():
            p = bodies.get(row["email_id"], {})
            body_ns, body_t, meta = audit_body(p)
            c = cmap.get(str(row["email_id"]), {})
            print("-" * 90)
            print(f"id={row['email_id']} n_q={row['n_questions']} bullets={row['n_bullets']} "
                  f"links={row['n_links']} words={row['n_words']} greet={row['greeting_style']} "
                  f"tmpl_rep={row['template_repeats']}")
            print(f"SUBJ: {p.get('hs_email_subject','')[:100]}")
            if name in ("n_questions", "no_questions", "subject_is_question"):
                print(f"  questions counted: {[q[:90] for q in audit_questions(body_t)][:4]}")
            if name == "n_links":
                print(f"  links: {[u[:70] for u in URL_RE.findall(body_ns)][:4]}")
            if name in ("mentions_company",):
                print(f"  contact company: {c.get('company')}")
            if name in ("name_beyond_greeting",):
                print(f"  firstname: {c.get('firstname')}")
            print("  BODY[:500]: " + body_ns[:500].replace("\n", " ⏎ "))


if __name__ == "__main__":
    main()
