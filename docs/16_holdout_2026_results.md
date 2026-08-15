# The 2026 holdout — opened once, 2026-08-15

Predictions P1–P9 (`docs/13`) and Q1–Q9 (`docs/14`) were committed before any 2026
outcome was read; decision rules were tightened blind in the audit (`docs/15` §1). This
document scores all 18 against those rules, unchanged. Population: 2026 cold pitches
n=1,286 (replied 6.5%, interested 4.4%) and event invites n=1,837 (replied 13.5%);
within-sender FE, cluster-robust SEs, identical code (`analyze_q1.py`, `analyze_q2.py`,
`length_control.py`).

**Process note, logged for the audit trail:** during opening, a `--tool hand` sensitivity
run was found to write its JSON to the same filename as the main run (the tag ignored the
flag), so the first numbers extracted were the hand-only subset mislabelled as the main
spec. Caught within minutes because `why_now`'s arm size (391) contradicted the audit's
committed power table (694). Tag fixed (`_handonly` suffix), main spec re-run, scored
below. Both variants were pre-committed in docs/15 §4, so no analytic choice was made
after seeing outcomes.

## Scorecard

| # | prediction | rule (as committed) | 2026 result | verdict |
|---|---|---|---|---|
| P1 | templated < non-templated | replicate AND confirm | **−3.8pp, p=0.005** (1.8% vs 8.0%); interested −3.5pp, p=0.001; 3/4 reps | **CONFIRMED, both outcomes** |
| P2 | short ≤100 > longer | replicate AND confirm (powered) | +0.8pp, p=0.64, CI [−2.7, +4.3] | **direction only — 2025's +4.5pp is excluded by the CI. Attenuated, not confirmed** |
| P3 | subject-question > not | direction only (underpowered, 79 emails) | +1.7pp | direction holds |
| P4 | bold < non-bold | direction only | +5.7pp, p=0.35 — wrong sign inside ±MDE | **inconclusive** (per rule) |
| P5 | name-again < not | untestable (2 emails in 2026) | — | untestable, as pre-declared |
| P6 | asks 2+ questions < fewer | direction only | −2.5pp | direction holds |
| P7a | invites: bullets − | replicate (powered) | +1.3pp, p=0.73; CI excludes 2025's −9.6 | **FAILED — refuted** |
| P7b | invites: templated − | replicate | −2.3pp, p=0.21 | direction holds |
| P7c | invites: short + | replicate | +1.3pp, p=0.51; CI excludes 2025's +17.5 | direction holds, magnitude refuted |
| P8 | touch-2 rate within ±2pp of touch 1; ≥85% of replies by touch 4 | holds/fails | 5.8% vs 6.0% (Δ0.2pp); 95.6% by touch 4 | **HOLDS, both clauses** |
| P9 | interested mirrors replied on P1–P3 | direction | −3.5 / +0.8 / +0.8 | **HOLDS** |
| Q1 | why_now + on replied AND interested | replicate AND confirm | **replied +2.9pp, p=0.047; interested +3.0pp, p=0.012** (8.5% vs 4.1%); 4/5 reps | **CONFIRMED, both outcomes** |
| Q2 | research_signal null | 95% CI upper < +3.0pp | +0.6pp, CI [−3.5, +4.7] | **inconclusive** (CI contains 0 and +3) |
| Q3 | bespokeness null | same | +2.1pp, CI [−3.6, +7.8] | **inconclusive** |
| Q4 | ask_clarity null | same | +0.9pp, CI [−3.0, +4.8] | **inconclusive** |
| Q5 | recipient_centricity + | replicate | **−0.4pp, p=0.85; CI [−4.9, +4.1] excludes 2025's +5.3** | **FAILED — refuted** |
| Q6 | economy & peer_tone stay null | report only (flagged dims) | −3.7 p=0.17; +1.9 p=0.45 | consistent |
| Q7 | pain & proof-industry stay null after length control | holds/fails | −2.6 p=0.26; −3.1 p=0.19 | **HOLDS** |
| Q8 | why_now within ±3pp of +4.6 | holds/fails | +2.9 ∈ [1.6, 7.6] | **HOLDS** |
| Q9 | why_now is the largest positive judged effect | holds/fails | ranked #1 (+2.9) | **HOLDS** |

**Tally: 9 held/confirmed · 4 direction-only · 4 inconclusive · 2 refuted · 1 untestable**
(P7 counted once per sub-prediction.)

## The two results that define the study

**Templating and why-now are real.** Both survived a year of data they could not have
been fitted to, at effect sizes inside their predicted bands, on both outcomes, in most
individual reps. Templated cold pitches: 1.8% reply vs 8.0% — and 0.0% interested vs
5.6%. An explicit reason for writing now: 8.5% vs 4.1%.

**The exploratory darling died exactly as the safeguards said it might.**
`recipient_centricity` (+5.3pp in 2025, survived every within-2025 check, +9.4pp in the
short-email subset) came back at **−0.4pp** on fresh data, with the 2025 effect size
excluded. It was labelled exploratory, moderate-reliability, small-cell — every one of
those flags was earned. This is the clearest possible demonstration of why the study
distinguishes primary from exploratory and why nothing exploratory is stated as a rule.

## Honest readings of the rest

- **Short ≤100 words attenuated.** Direction survives (7.0% vs 5.9% raw) but the 2026 CI
  excludes the 2025 effect. Possible real drift (the 2026 mailbox mix is 44% tool-sent
  and less templated), possible 2025 overestimate. The report says "short is directionally
  better; the 4–5pp version of the claim did not survive."
- **The invite-formatting effects (bullets −9.6, short +17.5) look like 2025 artefacts**
  — 2026 invites show nothing of the kind. Only templating carries over. Anyone tempted
  to conclude "bullets kill invites" from 2025 now has the counter-evidence in hand.
- **The three personalisation nulls stay nulls but could not be certified as ≤3pp** —
  clustered SEs came in wider than the audit's planning approximation, so the equivalence
  test returned inconclusive rather than passed. What CAN be said: in two years of data,
  personalisation never once produced a significant positive effect, and 2026's point
  estimates (+0.6 to +2.5) are again small.
- **Sensitivity (pre-committed):** templated holds in the hand-sent-only subset (−2.9,
  p=0.004). why_now attenuates there (+1.6, p=0.54, n=725) — its 2026 signal is
  concentrated in the tool-assisted mail; noted, not explained away.
- **Q2 curve, 2026:** opener 5.8%, touch-2 6.0%, cumulative 11.4% — the "follow-up #1 is
  worth as much as the opener" pattern replicates.

## Status

The holdout is spent. No further 2026 test is legitimate; anything new needs post-Jul-2026
data. Next: results package for the operator, then the report — structured WITH him.
