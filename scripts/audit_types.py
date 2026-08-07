"""Audit the type classifier: print 20 random examples of each assigned type,
with the text the classifier saw, so the assignment can be read and judged.

The brief requires reading examples of each type before trusting any
reply-rate-by-type number.

Usage: python3 audit_types.py [n_per_type]
"""
import glob
import json
import os
import random
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "output")


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    labels = {}
    for p in glob.glob(os.path.join(OUT, "type_labels", "batch_*.json")):
        for x in json.load(open(p)):
            labels[str(x["id"])] = x
    items = {}
    for p in glob.glob(os.path.join(OUT, "type_batches", "batch_*.json")):
        for x in json.load(open(p)):
            if str(x["id"]) in labels:
                items[str(x["id"])] = x

    by_type = {}
    for i, lab in labels.items():
        by_type.setdefault(lab["type"], []).append(i)

    for t, ids in sorted(by_type.items()):
        random.Random(41).shuffle(ids)
        print("\n" + "#" * 92)
        print(f"### TYPE AUDIT: {t} — {len(ids)} assigned, showing {min(n, len(ids))}")
        for i in ids[:n]:
            it = items[i]
            print("-" * 92)
            print(f"id={i} reply_like={labels[i].get('is_reply_like')}")
            print(f"SUBJ: {it['subject'][:110]}")
            print("TEXT: " + it["text"][:600].replace("\n", " ⏎ "))


if __name__ == "__main__":
    main()
