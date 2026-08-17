"""Effect estimate for why_now_grade — runs ONLY if the reliability gate passed.

The gate is a structural block, not a promise: this script imports whynow_agreement and
refuses to compute a single effect if kappa on the pre-declared split is below 0.50. The
threshold was fixed in rules/judge_rubric.md at 041ee6c, before any email was graded,
because the failure mode named by the operator was seeing an interesting effect first and
deciding the reliability was good enough afterwards.

Contrasts, both pre-declared before any outcome was joined:
  PRIMARY   top-2-box (4-5) vs (1-3), restricted to grade >= 1, cold pitches.
            Grade 0 is excluded: "occasion vs none" is the confirmed binary finding, and
            re-running it here would be that same test under a new name.
  SECONDARY templated vs hand-written grade depth — does templating shallow the occasion
            rather than remove it (docs/18 §C1 found presence is identical at 70.7/71.8%).

Everything here is EXPLORATORY. The 2026 hold-out was opened on 2026-08-15 and is spent;
a 2026 number below is a second look at used data and cannot confirm anything.

Usage: python3 whynow_grade_analysis.py [--G 30]
"""
import argparse
import os
import sys

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import whynow_agreement as wa

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
GATE = wa.GATE


def gate_value():
    """Recompute the gate here. Cheap, and it means the block cannot be bypassed."""
    a = wa.load_dir(wa.A_DIR).rename(columns={"why_now_grade": "ga"})
    b = wa.load_dir(wa.B_DIR).rename(columns={"why_now_grade": "gb"})
    m = a.merge(b, on="email_id", how="inner")
    both = m[(m["ga"] >= 1) & (m["gb"] >= 1)]
    return wa.kappa(both["ga"] >= 4, both["gb"] >= 4), len(both)


def fe(df, mask, outcome):
    """§3 primary spec, unchanged: LPM, sender fixed effects, SEs clustered on sender."""
    d = pd.DataFrame({"y": df[outcome].astype(float), "x": mask.astype(float),
                      "s": df["sender_local"]})
    if d["x"].nunique() < 2 or d["s"].nunique() < 2:
        return np.nan, np.nan, np.nan
    m = smf.ols("y ~ x + C(s)", data=d).fit(cov_type="cluster",
                                            cov_kwds={"groups": d["s"]})
    return m.params["x"], m.bse["x"], m.pvalues["x"]


def load(G):
    df = pd.read_parquet(os.path.join(DATA, f"frame_G{G}.parquet"))
    df["email_id"] = df["email_id"].astype(str)
    g = pd.read_parquet(os.path.join(DATA, "whynow_grade.parquet"))
    g["email_id"] = g["email_id"].astype(str)
    df = df.merge(g, on="email_id", how="left")
    j = pd.read_parquet(os.path.join(DATA, "judge_scores.parquet"))[["email_id", "why_now"]]
    j["email_id"] = j["email_id"].astype(str)
    df = df.merge(j, on="email_id", how="left")
    fe_p = os.path.join(DATA, "features_openers.parquet")
    if os.path.exists(fe_p):
        f = pd.read_parquet(fe_p)
        f["email_id"] = f["email_id"].astype(str)
        keep = [c for c in ["email_id", "is_template_3plus"] if c in f.columns]
        df = df.merge(f[keep], on="email_id", how="left")
    df["yr"] = pd.to_datetime(df["opener_ts"]).dt.year
    return df[df["type"] == "cold_pitch"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--G", type=int, default=30)
    args = ap.parse_args()

    k, n_gate = gate_value()
    print(f"reliability gate: kappa {k:.3f} on n={n_gate} (threshold {GATE:.2f})")
    if not (k >= GATE):
        print(f"\nGATE FAILED — refusing to estimate any effect. The graded scale is "
              f"binned per rules/judge_rubric.md. Nothing from it enters a deliverable.")
        return 1
    print("gate passed; proceeding.\n")

    df = load(args.G)
    print(f"cold pitches with a grade: {df['why_now_grade'].notna().sum()} of {len(df)}\n")

    for outcome in ("replied", "interested"):
        print("=" * 78)
        print(f"OUTCOME: {outcome}")
        for yr in (2025, 2026):
            d = df[(df["yr"] == yr) & df["why_now_grade"].notna()].copy()
            tag = "training" if yr == 2025 else "SPENT hold-out — exploratory only"
            print(f"\n--- {yr}  (n={len(d)})  [{tag}] ---")

            t = d.groupby("why_now_grade")[outcome].agg(["size", "sum"])
            t["rate %"] = (100 * t["sum"] / t["size"]).round(1)
            print("  reply rate by grade:")
            print("  " + t.to_string().replace("\n", "\n  "))

            sub = d[d["why_now_grade"] >= 1]
            b, se, p = fe(sub, sub["why_now_grade"] >= 4, outcome)
            n_hi = int((sub["why_now_grade"] >= 4).sum())
            print(f"\n  PRIMARY  4-5 vs 1-3 among grade>=1:  "
                  f"{100 * b:+.2f}pp  (SE {100 * se:.2f}, p={p:.4f})   "
                  f"n_hi={n_hi} n_lo={len(sub) - n_hi}")

            b0, se0, p0 = fe(d, d["why_now_grade"] >= 1, outcome)
            print(f"  context  grade>=1 vs 0 (the old binary, restated): "
                  f"{100 * b0:+.2f}pp (p={p0:.4f})")
            if d["why_now"].notna().any():
                bb, _, pb = fe(d, d["why_now"] == True, outcome)
                print(f"  context  binary why_now as committed:               "
                      f"{100 * bb:+.2f}pp (p={pb:.4f})")

    print("\n" + "=" * 78)
    print("SECONDARY: does templating shallow the occasion, or only remove it?")
    print("docs/18 §C1: presence is identical (70.7% templated vs 71.8% hand). Depth:")
    if "is_template_3plus" not in df.columns:
        print("  is_template_3plus not available — cannot run")
        return 0
    for yr in (2025, 2026):
        d = df[(df["yr"] == yr) & df["why_now_grade"].notna()]
        tp, hw = d[d["is_template_3plus"] == True], d[d["is_template_3plus"] != True]
        print(f"\n--- {yr} ---   templated n={len(tp)}  hand-written n={len(hw)}")
        print(f"  mean grade          {tp['why_now_grade'].mean():.2f}  vs  "
              f"{hw['why_now_grade'].mean():.2f}")
        print(f"  share grade >=1     {100 * (tp['why_now_grade'] >= 1).mean():.1f}%  vs  "
              f"{100 * (hw['why_now_grade'] >= 1).mean():.1f}%")
        print(f"  share grade 4-5     {100 * (tp['why_now_grade'] >= 4).mean():.1f}%  vs  "
              f"{100 * (hw['why_now_grade'] >= 4).mean():.1f}%")
        print(f"  share 4-5 among >=1 "
              f"{100 * (tp[tp['why_now_grade'] >= 1]['why_now_grade'] >= 4).mean():.1f}%"
              f"  vs  "
              f"{100 * (hw[hw['why_now_grade'] >= 1]['why_now_grade'] >= 4).mean():.1f}%")
        b, se, p = fe(d, d["is_template_3plus"] == True, "why_now_grade")
        print(f"  within-sender, templated -> grade: {b:+.3f} grades "
              f"(SE {se:.3f}, p={p:.4f})")
        dd = d[d["why_now_grade"] >= 1]
        b2, se2, p2 = fe(dd, dd["is_template_3plus"] == True, "why_now_grade")
        print(f"  same, among grade>=1 only:         {b2:+.3f} grades (p={p2:.4f})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
