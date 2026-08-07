"""Generic body puller — batch-reads full bodies for a list of email ids. READ-ONLY.

Usage: python3 pull_bodies.py <ids.txt> <out_name.jsonl.gz>
ids.txt: one HubSpot email engagement id per line.
Resumable: appends in shards; already-fetched ids are skipped on rerun.
"""
import gzip
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hs import load_token, batch_read

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

PROPS = ["hs_timestamp", "hs_email_direction", "hs_email_subject", "hs_email_text",
         "hs_email_html", "hs_body_preview", "hs_email_from_email", "hs_email_to_email",
         "hs_email_thread_id", "hs_incoming_email_is_out_of_office"]

SHARD = 5000


def main():
    ids_file, out_name = sys.argv[1], sys.argv[2]
    out_path = os.path.join(DATA, out_name)
    ids = [l.strip() for l in open(ids_file) if l.strip()]
    ids = list(dict.fromkeys(ids))

    have = set()
    if os.path.exists(out_path):
        with gzip.open(out_path, "rt") as f:
            for line in f:
                have.add(json.loads(line)["id"])
    todo = [i for i in ids if i not in have]
    print(f"{len(ids)} requested, {len(have)} already on disk, {len(todo)} to fetch", flush=True)

    token = load_token()
    for s in range(0, len(todo), SHARD):
        chunk = todo[s:s + SHARD]
        rows = batch_read("emails", chunk, token, PROPS, throttle=0.06)
        with gzip.open(out_path, "at") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
        print(f"  shard done: {s + len(chunk)}/{len(todo)} (+{len(rows)} rows)", flush=True)
    print("BODIES PULL COMPLETE", flush=True)


if __name__ == "__main__":
    main()
