"""The reliability gate for why_now_grade — declared in rules/judge_rubric.md at 041ee6c,
before a single email was graded.

  GATE: Cohen's kappa on the 4-5 vs 1-3 split (the split the analysis uses), among items
        both runs graded >= 1.
        >= 0.50 -> the scale is usable
        <  0.50 -> the scale is BINNED. No effect estimate from it enters any deliverable
                   and the failure is written up.

Three further numbers are printed with no gate attached, because they describe the
instrument rather than the result: the unconditioned 4-5 vs 0-3 kappa, the 0 vs >=1 kappa,
and agreement between grade 0 and the binary why_now == false from the Layer-2 pass.

WHY KAPPA AND NOT RAW AGREEMENT — the lesson is already in the record and is not being
relearned. `economy` agrees 75.8% and has kappa 0.22, because 88% of its mass sits in one
box; two raters agreeing on nothing but the base rate would still "agree" most of the time.

THIS SCRIPT NEVER OPENS THE FRAME. That is the operational enforcement of "the gate is
evaluated before any reply outcome is joined". data/judge_scores.parquet is read for the
binary comparison, and it contains no outcome.

Usage: python3 whynow_agreement.py
Exit:  0 = gate passed, 1 = gate failed (scale binned)
"""
import glob
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GATE = 0.50

A_DIR = "output/judge_scores_whynow"
B_DIR = "output/judge_scores_whynow_rescore"


def load_dir(d):
    rows = {}
    for p in sorted(glob.glob(os.path.join(ROOT, d, "batch_*.json"))):
        for r in json.load(open(p)):
            rows[str(r["id"])] = r
    df = pd.DataFrame(list(rows.values()))
    return df.assign(email_id=df["id"].astype(str)).drop(columns=["id"])


def kappa(a, b):
    """Cohen's kappa for two binary raters."""
    a, b = np.asarray(a, bool), np.asarray(b, bool)
    if len(a) == 0:
        return np.nan
    po = (a == b).mean()
    pe = a.mean() * b.mean() + (1 - a.mean()) * (1 - b.mean())
    return np.nan if pe == 1 else (po - pe) / (1 - pe)


def line(label, a, b, n_note=""):
    k = kappa(a, b)
    agree = 100 * (np.asarray(a, bool) == np.asarray(b, bool)).mean() if len(a) else np.nan
    print(f"  {label:<34} n={len(a):>4}  raw agree {agree:5.1f}%  kappa {k:.3f} {n_note}")
    return k


def main():
    a = load_dir(A_DIR).rename(columns={"why_now_grade": "ga", "evidence": "ea"})
    b = load_dir(B_DIR).rename(columns={"why_now_grade": "gb", "evidence": "eb"})
    m = a.merge(b, on="email_id", how="inner")
    print(f"main pass {len(a)} graded | rescore {len(b)} graded | overlap {len(m)}\n")
    assert len(m) > 500, f"overlap too small to measure the gate: {len(m)}"

    print("=== grade distributions on the overlap ===")
    dist = pd.DataFrame({
        "run A": m["ga"].value_counts().sort_index(),
        "run B": m["gb"].value_counts().sort_index(),
    }).fillna(0).astype(int)
    dist["A %"] = (100 * dist["run A"] / len(m)).round(1)
    dist["B %"] = (100 * dist["run B"] / len(m)).round(1)
    print(dist.to_string())
    print(f"\n  exact-grade match {100 * (m['ga'] == m['gb']).mean():.1f}%"
          f"   within-1 {100 * ((m['ga'] - m['gb']).abs() <= 1).mean():.1f}%"
          f"   mean A {m['ga'].mean():.2f} vs B {m['gb'].mean():.2f}")

    print("\n=== THE GATE (pre-declared) ===")
    both = m[(m["ga"] >= 1) & (m["gb"] >= 1)]
    k_gate = line("4-5 vs 1-3, both graded >=1", both["ga"] >= 4, both["gb"] >= 4,
                  "<-- GATE")

    print("\n=== ungated instrument checks ===")
    line("4-5 vs 0-3, unconditioned", m["ga"] >= 4, m["gb"] >= 4)
    line("0 vs >=1 (does an occasion exist)", m["ga"] >= 1, m["gb"] >= 1)

    jp = os.path.join(ROOT, "data", "judge_scores.parquet")
    if os.path.exists(jp):
        j = pd.read_parquet(jp)[["email_id", "why_now"]]
        j["email_id"] = j["email_id"].astype(str)
        mm = a.merge(j, on="email_id", how="inner")
        line("graded >=1 vs binary why_now (run A)", mm["ga"] >= 1, mm["why_now"])
        xt = pd.crosstab(mm["ga"], mm["why_now"])
        print("\n  grade x binary why_now, full population:")
        print("  " + xt.to_string().replace("\n", "\n  "))

    print("\n=== 8 disagreements, read them ===")
    d = both[(both["ga"] >= 4) != (both["gb"] >= 4)].head(8)
    for _, r in d.iterrows():
        print(f"  {r['email_id']}  A={r['ga']} \"{r['ea']}\"")
        print(f"  {'':>12}  B={r['gb']} \"{r['eb']}\"")

    print("\n" + "=" * 70)
    if np.isnan(k_gate):
        print("GATE UNMEASURABLE — degenerate split. Treated as a FAILURE.")
        return 1
    if k_gate >= GATE:
        print(f"GATE PASSED: kappa {k_gate:.3f} >= {GATE:.2f}. The graded scale is usable;"
              f" proceed to the effect estimate.")
        return 0
    print(f"GATE FAILED: kappa {k_gate:.3f} < {GATE:.2f}. The graded scale is BINNED.")
    print("No effect estimate from it may enter any deliverable. Write up the failure.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
