# Round 2 (Layer 2) findings — judged qualities, 2025, committed before 2026 opens

Run 2026-08-15. 12,462 openers scored blind on 12 dimensions by Sonnet, per
`rules/judge_rubric.md` (endpoints and middle anchors both committed before scoring).
Analysis on **2025 cold pitches only** (n=5,153; replied 6.9%, interested 4.7%).
Primary estimate is within-sender (sender fixed effects, cluster-robust SEs).
Benjamini–Hochberg applied **within each pre-registered family separately** — counted,
primary, exploratory — never pooled.

## First: how much of this can be believed

Three checks ran before any result was read.

**Halo (§4): PASSED — the dimensions are separable.** Mean pairwise |r| = 0.188 against a
0.60 threshold; PC1 explains 28.4% against 50%. The judge is not simply scoring "good
email" twelve times. One exception: `research_signal` and `bespokeness` correlate at
**+0.83** and are treated as one finding, not two.

**Repeatability (`judge_rubric.md` mechanics + §4b): two dimensions FAILED.** 1,246 emails
re-scored by a second Sonnet pass, 1,000 scored independently by Fable. Agreement is
reported as Cohen's kappa on the **top-2-box split the analysis actually uses**, because
raw agreement is inflated when a split is lopsided — `economy` puts 88% of emails in the
top box, so two raters agreeing on nothing but the base rate would still "agree" ~79% of
the time.

| dimension | kappa (self) | kappa (Fable) | verdict |
|---|---|---|---|
| research_signal | 0.749 | 0.735 | solid |
| why_now | 0.716 | 0.725 | solid |
| pain_hypothesis | 0.694 | 0.642 | solid |
| value_specificity | 0.665 | 0.621 | solid |
| proof_relevance | 0.650 | 0.662 | solid |
| bespokeness | 0.564 | 0.602 | moderate |
| recipient_centricity | 0.435 | 0.445 | moderate |
| polish | 0.428 | 0.460 | moderate |
| ask_clarity | 0.421 | 0.570 | moderate |
| **peer_tone** | **0.320** | **0.318** | **FLAGGED** |
| **economy** | **0.220** | **0.256** | **FLAGGED** |

**The most useful number here is the gap between the two columns: −0.016, i.e. none.**
Fable agrees with Sonnet almost exactly as well as Sonnet agrees with itself. So
`economy` and `peer_tone` are not a Sonnet weakness that a better model would fix — they
are ambiguous *questions*. "Does every sentence earn its place" does not have a stable
answer across careful readers. Both are flagged and every conclusion resting on them is
downgraded, per the pre-registered rule. Neither produced a significant result anyway.

**Judged-vs-counted overlap (added before interpretation).** A judged dimension that
restates a Layer-1 counter would let one effect be reported twice. Measured:
`economy ~ n_words` −0.48, `ask_size ~ subject_words` +0.48, `proof_relevance ~ n_words`
+0.42, `bespokeness ~ is_template_3plus` −0.31. Consequences are applied below.

## Primary family — 4 dimensions named in advance

| dimension | replied | interested | reps agreeing | q (replied) |
|---|---|---|---|---|
| **states a reason for reaching out now (`why_now`)** | **+4.6pp** | **+3.4pp** | **10/11 and 11/11** | **<0.0001** |
| bespokeness (top-2) | +1.9pp | +1.2pp | 5/9 | 0.29 — null |
| research_signal (top-2) | +1.3pp | +1.1pp | 5/12 | 0.46 — null |
| ask_clarity (top-2) | −0.0pp | +1.0pp | 7/13 | 0.99 — null |

**One of the four survives, and it is the strongest single result in the study.** Emails
with an explicit, checkable occasion for making contact — a launch, an event, a visit, a
named referral — reply at 7.9% against 4.6% without one. It holds on both outcomes, in
10 of 11 and 11 of 11 individual reps, on a dimension with solid repeatability
(kappa 0.72), and it **survives controlling for email length** (+4.1pp, p<0.0001).

The three nulls matter as much. **Personalisation, as this rubric measures it, did not
move reply rates.** Emails that cite a concrete researched fact about the recipient did
no better than emails that don't (+1.3pp, q=0.46). Since `research_signal` and
`bespokeness` are the same finding (r=0.83), that is one null stated twice, and it
contradicts the most repeated advice in outbound sales. It is also the dimension the
prior SAO study expected to survive.

## Exploratory family — never stated as a rule, reported with effect sizes

| dimension | replied | q | length-controlled | verdict |
|---|---|---|---|---|
| recipient_centricity (top-2) | **+5.3pp** | 0.0008 | **+5.0pp, p=0.0001** | survives; moderate reliability, small cell (n=388) |
| names any customer proof | **−6.1pp** | 0.013 | −3.7pp, p=0.12 | ambiguous — see below |
| value_specificity (top-2) | −3.6pp | 0.027 | −2.8pp, p=0.036 | weakly survives |
| proof matches their industry | −2.8pp | 0.009 | −1.2pp, p=0.21 | **is length, not proof** |
| pain_hypothesis (top-2) | −1.9pp | 0.041 | −0.9pp, p=0.28 | **is length, not pain** |
| polish (top-2) | +1.5pp | 0.18 | — | null |
| economy (top-2) | +0.2pp | 0.83 | — | null AND unreliable |
| peer_tone (top-2) | −0.8pp | 0.56 | — | null AND unreliable |

**The length control is a post-hoc diagnostic, not a pre-registered test**, and is reported
as such. It exists because the overlap check showed `proof_relevance` correlates +0.42
with word count: emails with more proof are longer, and Layer 1 already established that
longer emails do worse. Without this check, "naming customer proof costs you 6 points"
would have been reported as a discovery when it is substantially the length finding again.

Two of the five negatives disappear once length is held flat. **"Proof matching their
industry" and "articulating their pain" are not independently harmful — they are markers
of a longer email.**

`names any customer proof` is genuinely ambiguous and is reported that way: it loses
significance under the length control (p=0.12) but is strongly negative among short
emails only (−6.2pp, p=0.0006, n=1,368). The two checks disagree. No claim is made.

`recipient_centricity` is the one exploratory finding that strengthens under every check
(+9.4pp among short emails alone). It is still exploratory, its repeatability is only
moderate (kappa 0.435), and only 7.5% of emails score in its top-2 box.

## What the corpus looks like, independent of outcome

| | share |
|---|---|
| has a genuine why-now | 80.3% |
| no pain hypothesis at all (score 1) | 60% |
| named proof matching the recipient's field (4–5) | 49% |
| mail-merge or near it (bespokeness ≤2) | 44% |
| well-polished (4–5) | 81% |
| recipient-centric (4–5) | 7.5% |

Reps write clean, well-formed, clearly-asked emails that are mostly about us.

## Committed predictions for the 2026 holdout

Same decision rule as Round 1: **replicates** = same sign in 2026; **confirmed** = same
sign and p < 0.05 uncorrected (2026 cold pitch is n≈1,286, a quarter of 2025, so
BH-level power is not expected).

| # | prediction (2026, cold_pitch) | expectation |
|---|---|---|
| Q1 | `why_now` positive on replied AND interested | replicate AND confirm |
| Q2 | `research_signal` top-2 shows no significant effect | null replicates |
| Q3 | `bespokeness` top-2 shows no significant effect | null replicates |
| Q4 | `ask_clarity` top-2 shows no significant effect | null replicates |
| Q5 | `recipient_centricity` positive | replicate; confirm is uncertain given the small cell |
| Q6 | `economy` and `peer_tone` produce no significant effect | null replicates |
| Q7 | `pain_hypothesis` and `proof matches industry`, length-controlled, stay non-significant | holds |
| Q8 | `why_now` effect size in 2026 lands within ±3pp of +4.6pp | holds |
| Q9 | Ranking: `why_now` is the largest positive judged effect on replied | holds |

Together with P1–P9 in `docs/13_layer1_2025_findings.md`, these are the complete set.
**2026 is opened once, for both rounds together, after this file is committed.**
