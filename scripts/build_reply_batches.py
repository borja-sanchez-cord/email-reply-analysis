"""Build blinded reply-classification batches per rules/reply_classifier_protocol.md.

Each batch file: JSON list of {id, subject, text} — cleaned reply text with quoted
trails stripped (the classifier must never see the outgoing email), no sender, no
date, no push context. Batch size ~80.

Usage: python3 build_reply_batches.py data/ids_rc_needed.txt output/reply_batches
"""
import gzip
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from text_clean import html_to_text, strip_quoted

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APOLLO_ANY = re.compile(r"^(\[Apollo\] \[[^\]]+\] \[[^\]]+\]|Email: (<<|>>))\s*")


def main():
    ids_file, out_dir = sys.argv[1], sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)
    need = set(l.strip() for l in open(ids_file) if l.strip())

    items = []
    empties = 0
    with gzip.open(os.path.join(ROOT, "data", "bodies_reply_cands.jsonl.gz"), "rt") as f:
        for line in f:
            r = json.loads(line)
            if r["id"] not in need:
                continue
            p = r["properties"]
            text = p.get("hs_email_text") or ""
            if not text.strip() and p.get("hs_email_html"):
                text, _ = html_to_text(p["hs_email_html"])
            text = strip_quoted(text)
            subj = APOLLO_ANY.sub("", p.get("hs_email_subject") or "")
            if not text.strip():
                empties += 1
            items.append({"id": r["id"], "subject": subj[:150], "text": text[:2000]})

    items.sort(key=lambda x: x["id"])
    B = 80
    n = 0
    for i in range(0, len(items), B):
        with open(os.path.join(out_dir, f"batch_{i // B:04d}.json"), "w") as f:
            json.dump(items[i:i + B], f, indent=0)
        n += 1
    print(f"{len(items)} replies -> {n} batches in {out_dir} ({empties} with empty text)")


if __name__ == "__main__":
    main()
