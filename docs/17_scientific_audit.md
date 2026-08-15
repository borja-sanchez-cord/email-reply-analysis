# Scientific-validity and data-cleaning audit

Run 2026-08-15, after the holdout was scored and the deliverables shipped, on the
operator's instruction. Six checks against the pipeline itself — not the deliverables
(audited separately, 70/70) and not the pre-registered analyses (placebo-tested). Every
check runs on the committed data; nothing here re-opens any analytic choice.

## A. Reply-window truncation — REAL BUT BOUNDED, and it strengthens rather than weakens

The corpus ends 2026-07-31, so late openers had less than the 90-day reply window:
July 2026 openers had 0–31 days, June 31–61. Measured latency: median human reply
arrives in ~2 days; **97.2% of replies arrive within 30 days** — so June is effectively
complete and only July is materially clipped.

Sensitivity: recomputing both confirmed findings with a **fair-window outcome** (human
reply within 30 days, identical for both years):

- templated 2026: −3.8 → **−4.1pp, p=0.004** (stronger)
- why_now 2026: +2.9 → **+3.3pp, p=0.024** (stronger)

Truncation biases 2026 *levels* slightly downward but not the comparisons; correcting it
sharpens both confirmations. The raw 2025-vs-2026 rate comparison (6.9% vs 6.5%) narrows
to 6.6% vs 6.2% on the fair window — the cross-year gap is real but small either way.

## B. Cross-route dedup — 0.1% residual, negligible

The dedup key floors timestamps to 2-hour blocks, so a Gmail record and a tool record of
the same send can straddle a boundary and both survive. Measured: **55 such pairs** and
161 same-channel rapid resends, out of 224,756 touches (0.1%). Effect: a handful of
double-counted touches in Q2 denominators. Immaterial; documented.

## C. Impossible timestamps — CLEAN, and the fast-reply smell test passes

Zero replies timestamped before their opener. 92 pushes have a first *candidate* reply
within 60 seconds — inspected: they are out-of-office auto-replies, **correctly labelled
`out_of_office` and correctly not counted**; those pushes show `replied` only because a
human answered later. One genuine oddity: a `Re: test` reply reveals **4 test-like
openers** (subject "test"/"Re: test") inside the 12,077-row frame. Immaterial at 0.03%;
flagged for exclusion in any future frame build rather than removed post-hoc now.

## D. Unit-of-analysis and model-form sensitivities — the grid

Threats: 7.2% of people were emailed by 2+ reps and people can appear in multiple pushes
(rows not independent); SEs cluster on ~23–30 senders (small-cluster risk); the linear
probability model is an approximation at a 7% base rate.

| spec | 2025 templated | 2025 why_now | 2026 templated | 2026 why_now |
|---|---|---|---|---|
| main (committed) | −5.4, p<.0001 | +4.6, p<.0001 | −3.8, p=.005 | +2.9, p=.047 |
| one push per person | −5.4, p<.0001 | +4.7, p<.0001 | −3.8, p=.006 | +2.8, p=.041 |
| cluster by recipient domain | −5.4, p<.0001 | +4.6, p<.0001 | −3.8, p=.010 | +2.9, **p=.104** |
| human reply ≤30d (fair window) | −5.1, p=.0001 | +4.6, p<.0001 | −4.1, p=.004 | +3.3, p=.024 |
| logit, sender FE | OR 0.43, p<.0001 | OR 2.14, p<.0001 | OR 0.38, **p=.058** | OR 1.62, **p=.067** |

**Reading.** 2025: both findings are bulletproof — every specification agrees to the
decimal. 2026 templated: robust (worst p=.058, on a logit that drops 261 rows to handle
separation, with the odds ratio still 0.38). **2026 why_now: confirmed by the letter of
the pre-committed rule (main spec, p=.047), and the sign holds everywhere, but two of
five alternative specifications lift p above .05.** The honest label is "confirmed, with
a fragile 2026 margin" — the 2025 evidence is overwhelming; the 2026 replication is
directionally consistent and statistically marginal. The report will carry this
qualifier. (The logit p-values are also conservative here: separation-trimming removes
the all-miss senders that carry signal.)

Small-cluster risk is additionally bounded by two facts: the placebo produced a 2.1%
false-positive rate through the same machinery, and the domain-cluster variant (~1,000+
clusters) agrees with the sender-cluster variant everywhere except the one marginal cell
above.

## E. Join semantics and coverage edges — verified

Judge coverage is 100.0% on cold pitches and event invites in both years, so the
left-join in the analysis cannot shunt unjudged rows into "without" arms for the
populations that matter. The 15 items dropped for having <8 ratable words after redaction
are 0.1% of the corpus and enter no judged contrast.

## F. Feature-input hygiene — clean

Zero empty bodies and zero <10-word bodies inside the frame (eligibility filtering
removed them before feature computation), so the "short ≤100 words" arm contains no
degenerate members. Recomputing the short effect excluding <10-word bodies is a no-op:
+4.5pp, p=0.001, identical to committed.

## Verdict

No committed number changes. Two items enter the record: the **why_now 2026 fragility
qualifier** (D) — the one substantive finding of this audit, to be carried into the
report next to the confirmation — and the 4 test-emails + 55 dedup pairs as known,
quantified, immaterial residuals. The truncation concern resolves in the study's favor:
on a fair window both confirmations get stronger.
