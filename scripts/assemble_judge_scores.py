"""Merge the Layer-2 judge batches into data/judge_scores.parquet.

Recovery is from the FILESYSTEM, never from what an agent reported
(docs/LEARNINGS_FOR_NEXT_RUN.md #11). Agent self-reported counts are not trusted:
in this run 3 of 312 batches returned 39 items for 40 inputs while reporting success,
which is the §5.3 defect — a silently dropped item would otherwise carry a NaN score
into the analysis and be quietly dropped from a comparison.

Invariants asserted here, all hard failures:
  - every input id has exactly one score row
  - no id appears twice
  - every numeric dimension is an integer in range (proof_relevance 0-5, others 1-5)
  - why_now is boolean, ask_size is one of the five declared levels
  - no score row exists for an id that was never in a batch

Usage: python3 assemble_judge_scores.py
"""
import glob
import json
import os

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "output")

SCALE_1_5 = ["research_signal", "value_specificity", "pain_hypothesis", "ask_clarity",
             "bespokeness", "polish", "economy", "peer_tone", "recipient_centricity"]
ASK_SIZES = {"no_ask", "tiny", "small", "medium", "large"}
BATCH_DIRS = [("output/judge_batches", "output/judge_scores"),
              ("output/judge_batches_gap", "output/judge_scores_gap")]


def load_ids(d):
    ids = set()
    for p in sorted(glob.glob(os.path.join(ROOT, d, "batch_*.json"))):
        ids.update(str(x["id"]) for x in json.load(open(p)))
    return ids


def main():
    want = load_ids("output/judge_batches")
    rows, seen = {}, 0
    for _, sd in BATCH_DIRS:
        for p in sorted(glob.glob(os.path.join(ROOT, sd, "batch_*.json"))):
            for r in json.load(open(p)):
                seen += 1
                rows[str(r["id"])] = r          # gap dir loads last and wins

    df = pd.DataFrame(list(rows.values()))
    df["email_id"] = df["id"].astype(str)
    df = df.drop(columns=["id"])

    missing = want - set(df["email_id"])
    extra = set(df["email_id"]) - want
    print(f"batch inputs: {len(want)}   score rows read: {seen}   unique: {len(df)}")
    print(f"missing: {len(missing)}   not-in-any-batch: {len(extra)}")
    assert not missing, f"§5.3 HARD FAILURE — unscored ids: {sorted(missing)[:20]}"
    assert not extra, f"score rows for ids never sent: {sorted(extra)[:20]}"
    assert df["email_id"].is_unique, "duplicate email_id in judge scores"

    for c in SCALE_1_5:
        bad = ~df[c].apply(lambda v: isinstance(v, (int,)) and 1 <= v <= 5)
        assert not bad.any(), f"{c}: {int(bad.sum())} values outside 1-5"
    bad = ~df["proof_relevance"].apply(lambda v: isinstance(v, (int,)) and 0 <= v <= 5)
    assert not bad.any(), f"proof_relevance: {int(bad.sum())} outside 0-5"
    assert df["why_now"].isin([True, False]).all(), "why_now not boolean"
    assert df["ask_size"].isin(ASK_SIZES).all(), "illegal ask_size"

    df.to_parquet(os.path.join(DATA, "judge_scores.parquet"), index=False)
    print(f"\nwrote data/judge_scores.parquet — {len(df)} rows\n")

    print("=== score distributions (blind: no outcome has been joined) ===")
    for c in SCALE_1_5 + ["proof_relevance"]:
        vc = df[c].value_counts().sort_index()
        share = " ".join(f"{k}:{100 * v / len(df):.0f}%" for k, v in vc.items())
        print(f"  {c:<22} mean {df[c].mean():.2f}   {share}")
    print(f"  {'why_now':<22} true {100 * df['why_now'].mean():.1f}%")
    print(f"  {'ask_size':<22} " +
          " ".join(f"{k}:{100 * v / len(df):.0f}%"
                   for k, v in df["ask_size"].value_counts().items()))


if __name__ == "__main__":
    main()
