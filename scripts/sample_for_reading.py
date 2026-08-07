"""Print random opener bodies for human/model reading — the read-before-classify step.

Usage: python3 sample_for_reading.py <bodies.jsonl.gz> <n> [seed] [--ids id1,id2,...]
Prints cleaned text (html→text, quoted trails stripped) with subject, id, ts.
No outcome information is printed anywhere here.
"""
import gzip
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from text_clean import html_to_text, strip_quoted

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")


def load_bodies(path):
    rows = []
    with gzip.open(os.path.join(DATA, path) if not path.startswith("/") else path, "rt") as f:
        for line in f:
            rows.append(json.loads(line))
    return rows


def clean(r):
    p = r["properties"]
    text = p.get("hs_email_text") or ""
    if not text.strip() and p.get("hs_email_html"):
        text, _ = html_to_text(p["hs_email_html"])
    return strip_quoted(text)


def main():
    path, n = sys.argv[1], int(sys.argv[2])
    seed = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3].isdigit() else 7
    rows = load_bodies(path)
    ids = None
    for a in sys.argv:
        if a.startswith("--ids="):
            ids = set(a.split("=", 1)[1].split(","))
    if ids:
        rows = [r for r in rows if r["id"] in ids]
    random.Random(seed).shuffle(rows)
    for r in rows[:n]:
        p = r["properties"]
        print("=" * 78)
        print(f"id={r['id']}  ts={p.get('hs_timestamp')}  dir={p.get('hs_email_direction')}")
        print(f"SUBJECT: {p.get('hs_email_subject')}")
        print("-" * 78)
        body = clean(r)
        print(body[:2500] if body.strip() else "(EMPTY BODY)")


if __name__ == "__main__":
    main()
