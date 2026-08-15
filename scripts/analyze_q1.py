"""Question 1 — reply rate with a feature vs without it, per the pre-registered plan.

For each feature: rate with, rate without, gap in percentage points, and a rough
range for the gap (95% interval on the difference of two proportions, reported in
plain words in the write-up). Plus the two robustness checks:

  within-rep : among reps with >= MIN_PER_ARM openers of both kinds, how many show
               the same direction ("7 of 9 reps")
  holdout    : the same table computed on 2026 (run separately with --year 2026)

Splits come from rules/analysis_splits_addendum.md — declared before any number
was computed. Nothing here chooses a threshold from the data.

Per RUN2_PREREGISTRATION §3 the primary specification is within-sender: a linear
probability model with sender fixed effects and cluster-robust SEs by sender
(fe_gap_pp / fe_p). The pooled with/without gap is reported alongside. BH
(Benjamini–Hochberg) is applied to the FE p-values across all reported features
in a run (§2's multiple-comparison rule, applied to the Layer-1 family).

--shuffle-seed N implements the §5.2 placebo: the outcome column is permuted
WITHIN sender before the identical analysis runs. Any bh_sig=True on shuffled
labels is a bug in this code, not a result.

Usage: python3 analyze_q1.py --type cold_pitch --year 2025 [--G 30] [--outcome replied]
                             [--ca confirmed_ca|fallback_ca] [--shuffle-seed N]
"""
import argparse
import json
import os

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "output")

MIN_PER_ARM = 20        # per-rep panel: reps need this many openers in EACH arm
MIN_CELL = 30           # don't report a feature whose smaller arm is below this

# (name, predicate) — every split declared in rules/analysis_splits_addendum.md
BINARY_FEATURES = [
    ("asks a question", lambda d: d["n_questions"] >= 1),
    ("asks 2+ questions", lambda d: d["n_questions"] >= 2),
    ("short (<=100 words)", lambda d: d["n_words"] <= 100),
    ("very short (<=60 words)", lambda d: d["n_words"] <= 60),
    ("long (>150 words)", lambda d: d["n_words"] > 150),
    ("few sentences (<=8)", lambda d: d["n_sentences"] <= 8),
    ("few paragraphs (<=4)", lambda d: d["n_paragraphs"] <= 4),
    ("short first question (<=12 words)", lambda d: (d["n_questions"] >= 1)
     & (d["first_question_words"] <= 12)),
    ("has a link", lambda d: d["n_links"] >= 1),
    ("has 2+ links", lambda d: d["n_links"] >= 2),
    ("has bullets", lambda d: d["n_bullets"] >= 1),
    ("has bold text", lambda d: d["has_bold"]),
    ("has an image", lambda d: d["n_images"] >= 1),
    ("short subject (<=4 words)", lambda d: d["subject_words"] <= 4),
    ("subject is a question", lambda d: d["subject_is_question"]),
    ("subject has their name", lambda d: d["subject_has_name"]),
    ("subject has their company", lambda d: d["subject_has_company"]),
    ("greets them by name", lambda d: d["greeting_has_name"]),
    ("uses their name again in the body", lambda d: d["name_beyond_greeting"]),
    ("mentions their company", lambda d: d["mentions_company"]),
    ("mentions their role/work", lambda d: d["mentions_role_words"]),
    ("templated (3+ identical bodies)", lambda d: d["is_template_3plus"]),
    ("informal greeting (hey)", lambda d: d["greeting_style"] == "hey"),
    ("no greeting", lambda d: d["greeting_style"].isin(["none", "name_only"])),
]

# judged dimensions are added dynamically if the judge output is present
JUDGE_TOPBOX = ["research_signal", "value_specificity", "pain_hypothesis", "ask_clarity",
                "bespokeness", "polish", "economy", "peer_tone", "recipient_centricity"]

# §2 fixes THREE separate Benjamini-Hochberg families. Pooling them would be a different
# (and more permissive) test than the one pre-registered:
#   counted    - the Layer-1 countable features
#   primary    - the 4 judged dimensions named in advance
#   exploratory- the remaining 8, never stated as a rule regardless of significance
PRIMARY_DIMS = {"research_signal", "why_now", "ask_clarity", "bespokeness"}

# Repeatability from scripts/judge_agreement.py (top-2-box Cohen's kappa, n=1,246
# same-model and n=1,000 cross-model). judge_rubric.md requires poorly repeatable
# dimensions to be flagged and any conclusion built on them downgraded.
KAPPA = {"research_signal": 0.749, "why_now": 0.716, "pain_hypothesis": 0.694,
         "value_specificity": 0.665, "proof_relevance": 0.650, "bespokeness": 0.564,
         "recipient_centricity": 0.435, "polish": 0.428, "ask_clarity": 0.421,
         "peer_tone": 0.320, "economy": 0.220}


def reliability(dim):
    k = KAPPA.get(dim)
    if k is None:
        return ""
    return "UNRELIABLE" if k < 0.4 else ("moderate" if k < 0.6 else "solid")

BUCKETS = {
    "word count": ("n_words", [0, 50, 100, 150, 250, 10 ** 9],
                   ["<50", "50-99", "100-149", "150-249", "250+"]),
    "questions": ("n_questions", [-1, 0, 1, 2, 10 ** 9], ["0", "1", "2", "3+"]),
    "links": ("n_links", [-1, 0, 1, 2, 10 ** 9], ["0", "1", "2", "3+"]),
    "subject words": ("subject_words", [0, 2, 4, 7, 10 ** 9], ["1-2", "3-4", "5-7", "8+"]),
    "sentences": ("n_sentences", [0, 4, 8, 12, 10 ** 9], ["1-4", "5-8", "9-12", "13+"]),
}


def wilson_diff(k1, n1, k2, n2, z=1.96):
    """95% interval for (p1 - p2), Newcombe's method from two Wilson intervals."""
    def wilson(k, n):
        if n == 0:
            return (np.nan, np.nan)
        p = k / n
        d = 1 + z * z / n
        c = (p + z * z / (2 * n)) / d
        h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
        return max(0.0, c - h), min(1.0, c + h)
    l1, u1 = wilson(k1, n1)
    l2, u2 = wilson(k2, n2)
    p1, p2 = (k1 / n1 if n1 else np.nan), (k2 / n2 if n2 else np.nan)
    lo = (p1 - p2) - np.sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2)
    hi = (p1 - p2) + np.sqrt((u1 - p1) ** 2 + (p2 - l2) ** 2)
    return lo, hi


def fe_estimate(df, mask, outcome):
    """§3 primary spec: LPM with sender fixed effects, SEs clustered by sender."""
    d = pd.DataFrame({"y": df[outcome].astype(float), "x": mask.astype(float),
                      "s": df["sender_local"]})
    if d["x"].nunique() < 2 or d["s"].nunique() < 2:
        return np.nan, np.nan, np.nan
    m = smf.ols("y ~ x + C(s)", data=d).fit(
        cov_type="cluster", cov_kwds={"groups": d["s"]})
    return m.params["x"], m.bse["x"], m.pvalues["x"]


def bh(pvals):
    """Benjamini–Hochberg q-values; NaN-safe."""
    p = np.asarray(pvals, dtype=float)
    q = np.full_like(p, np.nan)
    ok = ~np.isnan(p)
    pv = p[ok]
    n = len(pv)
    if n == 0:
        return q
    order = np.argsort(pv)
    ranked = pv[order] * n / (np.arange(n) + 1)
    ranked = np.minimum.accumulate(ranked[::-1])[::-1]
    out = np.empty(n)
    out[order] = np.minimum(ranked, 1.0)
    q[ok] = out
    return q


def within_rep(df, mask, outcome):
    """Direction of the effect inside each rep who sent both kinds.

    Returns the count of reps with a POSITIVE gap. Callers must compare that against
    the sign of the effect: for a negative effect, 1-of-9-positive means 8 of 9 reps
    agree with it. Reported as `reps_agreeing` below so the table cannot be misread as
    "only 1 of 9 reps supports this".
    """
    agree = total = 0
    details = []
    for rep, g in df.groupby("sender_local"):
        m = mask.loc[g.index]
        a, b = g[m], g[~m]
        if len(a) < MIN_PER_ARM or len(b) < MIN_PER_ARM:
            continue
        total += 1
        d = a[outcome].mean() - b[outcome].mean()
        if d > 0:
            agree += 1
        details.append((rep, len(a), len(b), round(d * 100, 1)))
    return agree, total, details


def analyse(df, outcome, judge_cols):
    rows = []
    features = [(n, f, "counted", None) for n, f in BINARY_FEATURES]
    for c in judge_cols:
        fam = "primary" if c in PRIMARY_DIMS else "exploratory"
        features.append((f"judged: {c} (top 2 of 5)", lambda d, c=c: d[c] >= 4, fam, c))
    if "why_now" in df.columns:
        features.append(("judged: states a reason for reaching out now",
                         lambda d: d["why_now"] == True, "primary", "why_now"))
    if "proof_relevance" in df.columns:
        features.append(("judged: names any customer/social proof",
                         lambda d: d["proof_relevance"] >= 1, "exploratory",
                         "proof_relevance"))
        features.append(("judged: proof matches their industry",
                         lambda d: d["proof_relevance"] >= 4, "exploratory",
                         "proof_relevance"))

    for name, fn, family, dim in features:
        try:
            mask = fn(df).fillna(False)
        except KeyError:
            continue
        a, b = df[mask], df[~mask]
        if min(len(a), len(b)) < MIN_CELL:
            rows.append({"feature": name, "family": family, "n_with": len(a),
                         "n_without": len(b), "note": "too few to report"})
            continue
        k1, n1 = int(a[outcome].sum()), len(a)
        k2, n2 = int(b[outcome].sum()), len(b)
        lo, hi = wilson_diff(k1, n1, k2, n2)
        agree, total, details = within_rep(df, mask, outcome)
        fe_b, fe_se, fe_p = fe_estimate(df, mask, outcome)
        rows.append({
            "feature": name, "family": family, "reliability": reliability(dim),
            "n_with": n1, "rate_with": round(100 * k1 / n1, 1),
            "n_without": n2, "rate_without": round(100 * k2 / n2, 1),
            "gap_pp": round(100 * (k1 / n1 - k2 / n2), 1),
            "gap_lo": round(100 * lo, 1), "gap_hi": round(100 * hi, 1),
            "fe_gap_pp": round(100 * fe_b, 1) if not np.isnan(fe_b) else np.nan,
            "fe_se_pp": round(100 * fe_se, 1) if not np.isnan(fe_se) else np.nan,
            "fe_p": round(fe_p, 4) if not np.isnan(fe_p) else np.nan,
            "reps_positive": agree, "reps_tested": total,
            "reps_agreeing": (agree if (fe_b or 0) >= 0 else total - agree),
            "rep_detail": details,
        })
    res = pd.DataFrame(rows)
    if "fe_p" in res.columns:
        # BH applied WITHIN each pre-registered family, never pooled across them (§2)
        res["bh_q"] = np.nan
        for fam in res["family"].dropna().unique():
            m = res["family"] == fam
            res.loc[m, "bh_q"] = np.round(bh(res.loc[m, "fe_p"].values), 4)
        res["bh_sig"] = res["bh_q"] < 0.05
    return res


def bucket_tables(df, outcome):
    out = {}
    for label, (col, edges, names) in BUCKETS.items():
        b = pd.cut(df[col], bins=edges, labels=names)
        t = df.groupby(b, observed=False)[outcome].agg(["size", "sum"])
        t["rate"] = (100 * t["sum"] / t["size"]).round(1)
        out[label] = t
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--type", default="cold_pitch")
    ap.add_argument("--year", type=int, default=2025)
    ap.add_argument("--G", type=int, default=30)
    ap.add_argument("--outcome", default="replied")
    ap.add_argument("--ca", default="", choices=["", "confirmed_ca", "fallback_ca"],
                    help="§3: results are reported split by ca_class, never pooled silently")
    ap.add_argument("--shuffle-seed", type=int, default=0,
                    help="§5.2 placebo: permute the outcome within sender, then run unchanged")
    ap.add_argument("--tag", default="")
    args = ap.parse_args()

    df = pd.read_parquet(os.path.join(DATA, f"frame_G{args.G}.parquet"))
    jp = os.path.join(DATA, "judge_scores.parquet")
    judge_cols = []
    if os.path.exists(jp):
        j = pd.read_parquet(jp)
        j["email_id"] = j["email_id"].astype(str)
        df = df.merge(j, on="email_id", how="left", suffixes=("", "_j"))
        judge_cols = [c for c in JUDGE_TOPBOX if c in df.columns]

    df = df[(df["type"] == args.type) & (df["year"] == args.year)]
    if args.ca:
        df = df[df["ca_class"] == args.ca]
    if args.shuffle_seed:
        # §5.2 placebo: break the feature-outcome link but preserve each sender's
        # base rate, matching the within-sender design being tested
        rng = np.random.default_rng(args.shuffle_seed)
        df = df.copy()
        df[args.outcome] = (df.groupby("sender_local")[args.outcome]
                            .transform(lambda s: rng.permutation(s.values)))
    label = "PLACEBO (shuffled labels) " if args.shuffle_seed else ""
    print(f"=== {label}{args.type} / {args.year} / outcome={args.outcome} / G={args.G}"
          f"{' / ' + args.ca if args.ca else ''} — "
          f"n={len(df)}, reply rate {100 * df[args.outcome].mean():.1f}% ===")
    if len(df) < 100:
        print("too small to analyse — reporting count only")
        return

    res = analyse(df, args.outcome, judge_cols)
    res_show = res[res["note"].isna()] if "note" in res.columns else res
    res_show = res_show.sort_values("gap_pp", ascending=False)
    cols = ["feature", "family", "reliability", "n_with", "rate_with", "n_without",
            "rate_without", "gap_pp", "gap_lo", "gap_hi", "fe_gap_pp", "fe_p", "bh_q",
            "bh_sig", "reps_agreeing", "reps_tested"]
    cols = [c for c in cols if c in res_show.columns]
    for fam in ("counted", "primary", "exploratory"):
        sub = res_show[res_show["family"] == fam] if "family" in res_show else res_show
        if not len(sub):
            continue
        print(f"\n--- {fam.upper()} family (BH applied within this family only) ---")
        print(sub[cols].to_string(index=False))
    if "note" in res.columns and res["note"].notna().any():
        print("\nnot reported (too few):",
              ", ".join(res[res["note"].notna()]["feature"]))
    if "bh_sig" in res.columns:
        for fam in ("counted", "primary", "exploratory"):
            m = res["family"] == fam
            if m.any():
                print(f"BH-significant [{fam}]: {int(res.loc[m, 'bh_sig'].fillna(False).sum())}"
                      f" of {int(res.loc[m, 'fe_p'].notna().sum())}")

    tag = args.tag or f"{args.type}_{args.year}_{args.outcome}_G{args.G}"
    if args.ca:
        tag += f"_{args.ca}"
    if args.shuffle_seed:
        tag += f"_placebo{args.shuffle_seed}"
    res.to_json(os.path.join(OUT, f"q1_{tag}.json"), orient="records", indent=1)

    print("\n=== bucket tables ===")
    for label, t in bucket_tables(df, args.outcome).items():
        print(f"\n{label}:")
        print(t.to_string())


if __name__ == "__main__":
    main()
