"""Judge repeatability and cross-model validation.

Two checks, both pre-registered:

  SAME-MODEL RE-SCORE (rules/judge_rubric.md, mechanics): a random 10% is scored a
  second time by a fresh agent. Per-dimension agreement is reported and dimensions
  with poor repeatability are flagged, with any conclusion built on them downgraded.
  This measures whether a model agrees with ITSELF, which flatters it — every model is
  fairly self-consistent. It is the weaker check and is kept because it is pre-registered.

  CROSS-MODEL (RUN2_PREREGISTRATION §4b): the same 1,000 emails scored independently by
  a second, more capable model. Two instruments, not one model twice.

WHY KAPPA AND NOT RAW AGREEMENT. The analysis splits every 1-5 dimension at top-2-box
(4-5 vs 1-3), so the number that matters is agreement ON THAT SPLIT, not on the raw
1-5 score. But raw agreement is inflated when a split is lopsided: `economy` puts 89%
of emails in the top-2 box, so two raters who agreed on nothing but the base rate would
still "agree" about 80% of the time. Cohen's kappa corrects for that chance agreement.

  kappa >= 0.6 substantial | 0.4-0.6 moderate | < 0.4 poor -> FLAG the dimension

A dimension can therefore pass on raw agreement and still fail here, which is the
point: it is the split the study actually uses.

Usage: python3 judge_agreement.py
"""
import glob
import json
import os

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "output")

SCALES = ["research_signal", "value_specificity", "proof_relevance", "pain_hypothesis",
          "ask_clarity", "bespokeness", "polish", "economy", "peer_tone",
          "recipient_centricity"]


def load_dir(d):
    rows = {}
    for p in sorted(glob.glob(os.path.join(ROOT, d, "batch_*.json"))):
        for r in json.load(open(p)):
            rows[str(r["id"])] = r
    return pd.DataFrame(list(rows.values())).assign(
        email_id=lambda x: x["id"].astype(str)).drop(columns=["id"])


def kappa(a, b):
    """Cohen's kappa for two binary raters."""
    a, b = np.asarray(a, bool), np.asarray(b, bool)
    n = len(a)
    if n == 0:
        return np.nan
    po = (a == b).mean()
    pe = a.mean() * b.mean() + (1 - a.mean()) * (1 - b.mean())
    return np.nan if pe == 1 else (po - pe) / (1 - pe)


def compare(base, other, label):
    m = base.merge(other, on="email_id", suffixes=("_a", "_b"))
    print(f"\n{'=' * 78}\n{label} — n={len(m)}\n{'=' * 78}")
    if not len(m):
        print("  no overlap")
        return None
    rows = []
    for c in SCALES:
        a, b = m[c + "_a"].astype(float), m[c + "_b"].astype(float)
        lo = 0 if c == "proof_relevance" else 1
        t2a, t2b = a >= 4, b >= 4
        rows.append({
            "dimension": c,
            "exact": round(100 * (a == b).mean(), 1),
            "within1": round(100 * ((a - b).abs() <= 1).mean(), 1),
            "top2_agree": round(100 * (t2a == t2b).mean(), 1),
            "top2_kappa": round(kappa(t2a, t2b), 3),
            "top2_rate_a": round(100 * t2a.mean(), 1),
            "top2_rate_b": round(100 * t2b.mean(), 1),
            "r": round(a.corr(b), 3),
        })
    w = m["why_now_a"].astype(bool), m["why_now_b"].astype(bool)
    rows.append({"dimension": "why_now", "exact": round(100 * (w[0] == w[1]).mean(), 1),
                 "within1": np.nan, "top2_agree": round(100 * (w[0] == w[1]).mean(), 1),
                 "top2_kappa": round(kappa(*w), 3),
                 "top2_rate_a": round(100 * w[0].mean(), 1),
                 "top2_rate_b": round(100 * w[1].mean(), 1), "r": np.nan})
    rows.append({"dimension": "ask_size",
                 "exact": round(100 * (m["ask_size_a"] == m["ask_size_b"]).mean(), 1),
                 "within1": np.nan, "top2_agree": np.nan, "top2_kappa": np.nan,
                 "top2_rate_a": np.nan, "top2_rate_b": np.nan, "r": np.nan})
    t = pd.DataFrame(rows)
    print(t.to_string(index=False))

    flagged = t[(t["top2_kappa"] < 0.4) & t["top2_kappa"].notna()]["dimension"].tolist()
    weak = t[(t["top2_kappa"] >= 0.4) & (t["top2_kappa"] < 0.6)]["dimension"].tolist()
    print(f"\n  FLAGGED (kappa < 0.4, conclusions downgraded): {flagged or 'none'}")
    print(f"  moderate (0.4-0.6, reported with the caveat) : {weak or 'none'}")
    return t


def main():
    base = pd.read_parquet(os.path.join(DATA, "judge_scores.parquet"))
    base["email_id"] = base["email_id"].astype(str)

    res = {}
    for d, label in (("output/judge_scores_rescore", "SAME-MODEL RE-SCORE (Sonnet vs Sonnet)"),
                     ("output/judge_scores_fable", "CROSS-MODEL (Sonnet vs Fable) — §4b")):
        if not glob.glob(os.path.join(ROOT, d, "batch_*.json")):
            print(f"\n!! {d} is empty — not run yet")
            continue
        t = compare(base, load_dir(d), label)
        if t is not None:
            res[d.split("_")[-1]] = t
            t.to_csv(os.path.join(OUT, f"judge_agreement_{d.split('_')[-1]}.csv"),
                     index=False)

    if len(res) == 2:
        print(f"\n{'=' * 78}\nSELF vs CROSS — the gap is the honest measure of instrument error"
              f"\n{'=' * 78}")
        a, b = res["rescore"], res["fable"]
        j = a.merge(b, on="dimension", suffixes=("_self", "_cross"))
        print(j[["dimension", "top2_kappa_self", "top2_kappa_cross"]].to_string(index=False))
        d = (j["top2_kappa_self"] - j["top2_kappa_cross"]).mean()
        print(f"\n  mean kappa drop from self-agreement to cross-model: {d:.3f}")
        print("  A large drop means the model is consistent but not necessarily correct.")


if __name__ == "__main__":
    main()
