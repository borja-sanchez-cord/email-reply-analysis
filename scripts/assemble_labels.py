"""Assemble + validate agent classification outputs.

- output/reply_labels/batch_*.json -> data/reply_labels.parquet
- output/type_labels/batch_*.json  -> data/type_labels.parquet

Validates: every id in the corresponding batch inputs is labelled exactly once with a
legal value; prints coverage and lists incomplete batches (for re-runs).
"""
import glob
import json
import os

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "output")
DATA = os.path.join(ROOT, "data")

REPLY_CATS = {"human", "out_of_office", "auto_ack", "bounce_dsn", "unsubscribe_bot",
              "calendar_bot", "security_scan", "other_bot", "unclear"}
INTENTS = {"wants_call", "asks_question", "wants_materials", "referral", "not_now",
           "not_interested", "unsubscribe_request", "who_is_this", "other_human", "n/a"}
TYPES = {"cold_pitch", "event_invite", "post_event_followup", "other"}


def assemble(kind, batches_dir, labels_dir, validate):
    inputs = {}
    for p in sorted(glob.glob(os.path.join(OUT, batches_dir, "batch_*.json"))):
        b = os.path.basename(p).replace(".json", "")
        inputs[b] = {x["id"] for x in json.load(open(p))}
    rows, bad_batches = [], []
    for b, ids in inputs.items():
        lp = os.path.join(OUT, labels_dir, b + ".json")
        if not os.path.exists(lp):
            bad_batches.append((b, "missing"))
            continue
        try:
            labels = json.load(open(lp))
        except Exception as e:
            bad_batches.append((b, f"unparseable: {e}"))
            continue
        got = {str(x.get("id")) for x in labels}
        legal = all(validate(x) for x in labels)
        if got != ids or not legal:
            bad_batches.append((b, f"coverage {len(got & ids)}/{len(ids)}"
                                   + ("" if legal else " + illegal values")))
        for x in labels:
            if str(x.get("id")) in ids and validate(x):
                rows.append(x)
    df = pd.DataFrame(rows).drop_duplicates("id")
    df["id"] = df["id"].astype(str)
    print(f"{kind}: {len(df)} labels from {len(inputs) - len(bad_batches)}/{len(inputs)} clean batches")
    if bad_batches:
        print(f"  needs re-run: {[b for b, _ in bad_batches]}")
        for b, why in bad_batches[:10]:
            print(f"    {b}: {why}")
    return df, [b for b, _ in bad_batches]


def main():
    r, bad_r = assemble(
        "reply", "reply_batches", "reply_labels",
        lambda x: x.get("category") in REPLY_CATS
        and (x.get("category") != "human" or x.get("intent") in INTENTS))
    if len(r):
        r = r.rename(columns={"id": "email_id"})
        r.to_parquet(os.path.join(DATA, "reply_labels.parquet"), index=False)
        print(r["category"].value_counts().to_string())
        print(r[r["category"] == "human"]["intent"].value_counts().to_string())

    t, bad_t = assemble(
        "type", "type_batches", "type_labels",
        lambda x: x.get("type") in TYPES and isinstance(x.get("is_reply_like"), bool))
    if len(t):
        t = t.rename(columns={"id": "email_id"})
        t.to_parquet(os.path.join(DATA, "type_labels.parquet"), index=False)
        print(t["type"].value_counts().to_string())

    json.dump({"reply": bad_r, "type": bad_t}, open(os.path.join(OUT, "label_gaps.json"), "w"))


if __name__ == "__main__":
    main()
