"""Length-controlled FE estimates for judged dimensions — the Q7 code path.

This check exists because the judged-vs-counted overlap (output/
judged_vs_counted_correlation.csv) showed proof_relevance correlates +0.42 with word
count: emails with more proof are longer, and Layer 1 established longer emails do
worse. Without the control, "naming proof costs you 6 points" would be the length
finding reported a second time.

It is a POST-HOC DIAGNOSTIC, not a pre-registered test, and is labelled as such in
docs/14. It was first run ad-hoc on 2025 (2026-08-15); this script freezes that exact
specification so the holdout run uses committed code, not a retyped snippet:

    y ~ x + n_words + n_words^2 + C(sender)     cluster-robust SE by sender
    plus the same estimate on the <=100-word subset only

Usage: python3 length_control.py --year 2025 [--outcome replied] [--G 30]
"""
import argparse
import os

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

CONTRASTS = [
    ("any proof (>=1)", lambda d: d["proof_relevance"] >= 1),
    ("proof matches industry (>=4)", lambda d: d["proof_relevance"] >= 4),
    ("value_specificity top2", lambda d: d["value_specificity"] >= 4),
    ("pain_hypothesis top2", lambda d: d["pain_hypothesis"] >= 4),
    ("why_now", lambda d: d["why_now"] == True),
    ("recipient_centricity top2", lambda d: d["recipient_centricity"] >= 4),
]


def fe(dd, extra=""):
    m = smf.ols(f"y ~ x + {extra} C(s)" if extra else "y ~ x + C(s)", data=dd).fit(
        cov_type="cluster", cov_kwds={"groups": dd["s"]})
    return 100 * m.params["x"], m.pvalues["x"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--year", type=int, required=True)
    ap.add_argument("--outcome", default="replied")
    ap.add_argument("--G", type=int, default=30)
    ap.add_argument("--type", default="cold_pitch")
    args = ap.parse_args()

    f = pd.read_parquet(os.path.join(DATA, f"frame_G{args.G}.parquet"))
    f["email_id"] = f["email_id"].astype(str)
    j = pd.read_parquet(os.path.join(DATA, "judge_scores.parquet"))
    j["email_id"] = j["email_id"].astype(str)
    d = f.merge(j, on="email_id")
    d = d[(d["type"] == args.type) & (d["year"] == args.year)]
    print(f"{args.type} / {args.year} / {args.outcome} — n={len(d)}")
    print(f"{'contrast':<32}{'raw FE':>10}{'p':>9}{'+len ctrl':>11}{'p':>9}"
          f"{'short-only':>12}{'p':>9}{'n_short':>9}")

    for name, fn in CONTRASTS:
        x = fn(d).fillna(False)
        base = pd.DataFrame({"y": d[args.outcome].astype(float),
                             "x": x.astype(float), "s": d["sender_local"],
                             "w": d["n_words"].astype(float)})
        if base["x"].nunique() < 2:
            print(f"{name:<32}{'—':>10}   no variation")
            continue
        b0, p0 = fe(base)
        b1, p1 = fe(base, extra="w + I(w**2) +")
        sh = base[base["w"] <= 100]
        if sh["x"].nunique() > 1 and min(sh["x"].sum(), (1 - sh["x"]).sum()) >= 30:
            b2, p2 = fe(sh)
        else:
            b2, p2 = np.nan, np.nan
        print(f"{name:<32}{b0:>+10.1f}{p0:>9.4f}{b1:>+11.1f}{p1:>9.4f}"
              f"{b2:>+12.1f}{p2:>9.4f}{len(sh):>9}")


if __name__ == "__main__":
    main()
