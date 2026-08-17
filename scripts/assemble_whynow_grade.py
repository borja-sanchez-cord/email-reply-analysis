"""Merge the graded why-now batches into data/whynow_grade.parquet.

Recovery is from the FILESYSTEM, never from what an agent reported
(docs/LEARNINGS_FOR_NEXT_RUN.md #11). 3 of 312 batches in the Layer-2 pass returned 39
items for 40 inputs while reporting success; the same invariants are asserted here.

Deliberately does NOT join any outcome. The rubric addendum makes the reliability gate
evaluable before reply data is seen, and that is enforced by this script and
whynow_agreement.py both being frame-free.

Usage: python3 assemble_whynow_grade.py
"""
import glob
import json
import os

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BATCHES = "output/judge_batches_whynow"
# The gap dir loads last and wins. 9 of 161 batches returned 39, 38 and 35 items for 40
# inputs while every agent reported success — the §5.3 defect, third occurrence. The 14
# dropped items were re-run through a byte-identical prompt.
SCORES = ["output/judge_scores_whynow", "output/judge_scores_whynow_gap"]


def load_ids(d):
    ids = set()
    for p in sorted(glob.glob(os.path.join(ROOT, d, "batch_*.json"))):
        ids.update(str(x["id"]) for x in json.load(open(p)))
    return ids


def load_scores(dirs):
    rows, seen = {}, 0
    for d in dirs:
        for p in sorted(glob.glob(os.path.join(ROOT, d, "batch_*.json"))):
            for r in json.load(open(p)):
                seen += 1
                rows[str(r["id"])] = r
    return rows, seen


def main():
    want = load_ids(BATCHES)
    rows, seen = load_scores(SCORES)

    df = pd.DataFrame(list(rows.values()))
    df["email_id"] = df["id"].astype(str)
    df = df.drop(columns=["id"])

    missing = want - set(df["email_id"])
    extra = set(df["email_id"]) - want
    print(f"batch inputs: {len(want)}   score rows read: {seen}   unique: {len(df)}")
    print(f"missing: {len(missing)}   not-in-any-batch: {len(extra)}")
    assert not missing, f"HARD FAILURE — ungraded ids: {sorted(missing)[:20]}"
    assert not extra, f"score rows for ids never sent: {sorted(extra)[:20]}"
    assert df["email_id"].is_unique, "duplicate email_id"

    bad = ~df["why_now_grade"].apply(lambda v: isinstance(v, int) and 0 <= v <= 5)
    assert not bad.any(), f"why_now_grade: {int(bad.sum())} values outside 0-5"

    df = df[["email_id", "why_now_grade", "evidence"]]
    df.to_parquet(os.path.join(ROOT, "data", "whynow_grade.parquet"), index=False)
    print(f"\nwrote data/whynow_grade.parquet — {len(df)} rows\n")

    print("=== grade distribution (blind: no outcome joined) ===")
    vc = df["why_now_grade"].value_counts().sort_index()
    for k, v in vc.items():
        print(f"  {k}: {v:>5}  {100 * v / len(df):5.1f}%  " + "#" * int(60 * v / len(df)))
    print(f"\n  mean {df['why_now_grade'].mean():.2f}"
          f"   share >=1 {100 * (df['why_now_grade'] >= 1).mean():.1f}%"
          f"   share 4-5 {100 * (df['why_now_grade'] >= 4).mean():.1f}%"
          f"   share 4-5 among >=1 "
          f"{100 * (df.loc[df['why_now_grade'] >= 1, 'why_now_grade'] >= 4).mean():.1f}%")

    print("\n=== two sample evidence strings per grade (readable audit) ===")
    for g in range(6):
        sub = df[df["why_now_grade"] == g]["evidence"].head(2).tolist()
        for e in sub:
            print(f"  {g}: {e}")


if __name__ == "__main__":
    main()
