"""§4 halo check + the judged-vs-counted overlap check. Run BEFORE any Layer-2 result.

Two questions, both about whether a "finding" is really one finding wearing twelve hats.

1. HALO (pre-registered, RUN2_PREREGISTRATION §4). If the judge is really scoring
   "is this a good email", the 12 dimensions collapse into one.
     - decision rule, fixed in advance: mean pairwise |r| >= 0.6 OR PC1 >= 50% of
       variance -> the report leads with a single composite craft score and treats
       per-dimension claims as non-separable.
     - the matrix is published either way.

2. JUDGED vs COUNTED (added 2026-08-15, before Layer-2 was interpreted). A judged
   dimension that is really a restatement of a Layer-1 counter would let the same
   effect be reported twice — once as "short emails do better" and again as "economy
   scores well" — which inflates the apparent number of independent findings. This is
   the same error the Layer-1 write-up already handles for bold/name-again vs
   templating (docs/13). Correlations are reported so a reader can see the overlap.

Neither analysis touches an outcome, so neither can burn the 2026 holdout.

Usage: python3 halo_check.py
"""
import os

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "output")

DIMS = ["research_signal", "why_now", "value_specificity", "proof_relevance",
        "pain_hypothesis", "ask_clarity", "ask_size", "bespokeness", "polish",
        "economy", "peer_tone", "recipient_centricity"]
ASK_ORD = {"no_ask": 0, "tiny": 1, "small": 2, "medium": 3, "large": 4}

COUNTED = ["n_words", "n_sentences", "n_paragraphs", "n_questions", "n_links",
           "n_bullets", "has_bold", "n_images", "subject_words", "subject_is_question",
           "greeting_has_name", "name_beyond_greeting", "mentions_company",
           "is_template_3plus"]


def numeric(df):
    d = df[DIMS].copy()
    d["why_now"] = d["why_now"].astype(float)
    d["ask_size"] = d["ask_size"].map(ASK_ORD).astype(float)
    return d.astype(float)


def main():
    j = pd.read_parquet(os.path.join(DATA, "judge_scores.parquet"))
    j["email_id"] = j["email_id"].astype(str)
    d = numeric(j)
    print(f"halo check on {len(d)} judged emails\n")

    C = d.corr()
    print("=== 12x12 correlation matrix ===")
    print(C.round(2).to_string())
    C.to_csv(os.path.join(OUT, "halo_correlation_matrix.csv"))

    iu = np.triu_indices(len(DIMS), k=1)
    pair = C.values[iu]
    mean_abs = float(np.nanmean(np.abs(pair)))

    Z = (d - d.mean()) / d.std(ddof=0)
    Z = Z.dropna()
    eig = np.linalg.eigvalsh(np.cov(Z.values, rowvar=False))[::-1]
    pc1 = float(eig[0] / eig.sum())

    print(f"\nmean pairwise |r| : {mean_abs:.3f}   (threshold 0.60)")
    print(f"PC1 variance share: {pc1:.3f}   (threshold 0.50)")
    collapse = mean_abs >= 0.6 or pc1 >= 0.5
    print(f"\nVERDICT: {'COLLAPSE' if collapse else 'SEPARABLE'} — "
          + ("report leads with one composite craft score; per-dimension claims are "
             "not separable" if collapse else
             "the 12 dimensions carry distinct information; per-dimension claims stand"))

    hi = sorted(((abs(C.values[i, k]), DIMS[i], DIMS[k], C.values[i, k])
                 for i, k in zip(*iu)), reverse=True)[:8]
    print("\nmost-correlated pairs:")
    for a, x, y, r in hi:
        print(f"  {r:+.2f}  {x} ~ {y}")

    # --- judged vs counted -----------------------------------------------------
    f = pd.read_parquet(os.path.join(DATA, "frame_G30.parquet"))
    f["email_id"] = f["email_id"].astype(str)
    cols = [c for c in COUNTED if c in f.columns]
    m = f[["email_id"] + cols].merge(j[["email_id"] + DIMS], on="email_id")
    md = numeric(m)
    print(f"\n=== judged vs counted, n={len(m)} ===")
    X = m[cols].astype(float)
    tab = pd.DataFrame({c: [X[c].corr(md[dim]) for dim in DIMS] for c in cols},
                       index=DIMS)
    print(tab.round(2).to_string())
    tab.to_csv(os.path.join(OUT, "judged_vs_counted_correlation.csv"))

    flat = [(abs(v), i, c, v) for i in tab.index for c, v in tab.loc[i].items()
            if pd.notna(v)]
    print("\nstrongest judged~counted overlaps (|r| >= 0.35 is worth a caveat):")
    for a, i, c, v in sorted(flat, reverse=True)[:10]:
        flag = "  <-- report as one finding" if a >= 0.35 else ""
        print(f"  {v:+.2f}  {i} ~ {c}{flag}")


if __name__ == "__main__":
    main()
