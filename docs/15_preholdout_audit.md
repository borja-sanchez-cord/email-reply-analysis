# Pre-holdout audit — run before 2026 was opened

Run 2026-08-15 on the operator's instruction, after the 18 predictions (P1–P9, Q1–Q9)
were committed but **before any 2026 outcome was read**. Everything in this document uses
only: 2025 data, 2026 sample sizes and feature/judge prevalences (both outcome-blind by
construction), and the committed artefacts. The audit had four parts; each found
something.

## 1. Power — several predictions were not falsifiable as written

Minimum detectable effect (80% power, α=0.05) computed from 2026 arm sizes and the 2025
base rate (6.9% replied; 15.1% for invites):

| prediction | 2026 arms | MDE | 2025 effect | verdict |
|---|---|---|---|---|
| P1 templated | 327 / 959 | 4.5pp | −5.4 | **powered** |
| P2 short ≤100 | 641 / 645 | 4.0pp | +4.5 | **powered** |
| P3 subject question | 79 / 1,207 | 8.2pp | +4.5 | underpowered → direction-only |
| P4 bold | 126 / 1,160 | 6.7pp | −4.3 | underpowered → direction-only |
| P5 name-again | **2** / 1,284 | — | −5.4 | **UNTESTABLE** |
| P6 asks 2+ questions | 115 / 1,171 | 6.9pp | −2.5 | underpowered → direction-only |
| Q1 why_now | 694 / 592 | 4.0pp | +4.6 | **powered** |
| Q2/Q3/Q4 nulls | ~700 / ~580 | 4.0pp | ~+1.5 | see equivalence rule below |
| Q5 recipient_centricity | 383 / 903 | 4.3pp | +5.3 | **powered** |
| P7a/b/c invites | ≥131 per arm | 4.7–9.1pp | −9.6 / −10.1 / +17.5 | **powered** |

**The defect this fixes:** Q2–Q4 predicted personalisation "shows no significant effect"
in 2026. On a quarter of the data, *everything* tends to show no significant effect —
the null would have "replicated" from low power alone and the holdout would have
confirmed nothing. Same for P3/P4/P6 stated as "replicate".

**Revised decision rules, fixed now, before looking:**

- **Null predictions (Q2, Q3, Q4):** the null replicates only if the 2026 95% CI for the
  FE gap has its **upper bound below +3.0pp**. If the CI contains both 0 and +3.0pp the
  result is **inconclusive** — reported as such, never as confirmation. The bound: below
  every actionable 2025 positive effect (+4.5pp and up), above the CI noise floor
  (±2.8pp at these arm sizes, so the rule is decidable).
- **Underpowered directional predictions (P3, P4, P6):** tested on **direction of the FE
  point estimate only**; "confirm" is off the table and a wrong sign inside ±MDE is
  reported as inconclusive, not refuted.
- **P5: untestable and recorded as such.** The behaviour itself vanished — 7.7% of 2025
  cold pitches reused the recipient's name mid-body; **0.2% (2 emails) in 2026**. That
  says the templates changed, and no test of the reply effect is possible.
- Q6 (economy/peer_tone nulls): report-only — the dimensions are FLAGGED unreliable, so
  neither confirmation nor refutation would mean much.
- All other predictions keep their committed replicate/confirm rules unchanged.

## 2. 2026 readiness — structurally clean, one interpretation hazard

- **Judge coverage 100.0%** on 2026 cold_pitch (1,286) and event_invite (1,837);
  99.8% frame-wide (the residue is the 15 items with <8 ratable words, dropped by design).
- Type labels 0% missing, both years. Features: none >5% NaN. Channel: the frame is
  mailbox-only by construction, so the sequencer-mix confound cannot enter it.
- **Hazard: the ca_class mix flipped** — 2025 is 33% confirmed-CA / 67% fallback;
  2026 is **69% / 31%**. Any raw 2025-vs-2026 comparison is confounded by who is
  sending. Consequence, fixed now: every prediction test runs within-sender (as
  committed) **and is also reported split by ca_class** per §3.
- **The 2026 emails are themselves different** (all outcome-blind prevalences):
  templated 54%→25%, subject-question 19%→6%, name-again 8%→0.2%, bespokeness top-2
  32%→51%, why_now 71%→54%, research_signal top-2 47%→57%. The org changed how it
  writes. This is why several arms shrank below power, and it belongs in the report as
  a finding about behaviour, not a nuisance.

## 3. Reproduction — every committed number reproduces

- `pytest`: 61/61.
- Frame headlines: 12,077 rows; 10.8% / 6.9% — exact match to RESUME.
- The apparent 6.8%-vs-6.9% cold-pitch discrepancy **reconciles**: RESUME's 6.8/4.6
  (n=6,439) pools both years; docs/13's 6.9/4.7 (n=5,153) is 2025 only. Both correct.
- Four headline FE gaps recomputed **by hand** (within-sender demeaning, no
  statsmodels): templated −5.40, short +4.51, why_now +4.57 replied / +3.42 interested —
  all match the committed values to 0.1pp via an independent code path.
- Q2 curve total 902 vs frame 903: **explained** — exactly one push (10 touches)
  replied after touch 8 and the curve caps at MAX_TOUCH=8. Benign, documented.
- Q7's length control was an ad-hoc snippet; it is now frozen as
  `scripts/length_control.py`, which reproduces the 2025 numbers exactly, so the
  holdout runs committed code.

## 4. Prediction-to-code walk-through

Every prediction maps to a committed command and column:

| predictions | command | quantity |
|---|---|---|
| P1–P6, Q1–Q6 | `analyze_q1.py --type cold_pitch --year 2026 --outcome {replied,interested}` | `fe_gap_pp`, `fe_p`, per-family `bh_q` |
| P7 | same with `--type event_invite` | same |
| P8 | `analyze_q2.py --year 2026` | touch-1 vs touch-2 conditional rates; cumulative-by-4 share |
| Q7 | `length_control.py --year 2026` | `+len ctrl` column |
| Q8, Q9 | Q1 run above | `why_now` fe_gap vs +4.6±3.0; rank among judged positives |
| ca_class splits | `--ca confirmed_ca` / `--ca fallback_ca` variants | §3 requirement |

The 95% CI for the equivalence rule is `fe_gap_pp ± 1.96 × fe_se_pp`, both already
emitted per feature.

## Verdict

2026 may be opened. The audit changed the *decision rules* for seven predictions
(Q2–Q4 to equivalence bounds, P3/P4/P6 to direction-only, P5 to untestable) — all
blind, all before any 2026 outcome was read — and changed no prediction's substance.
Had it not run, the holdout would have "confirmed" three nulls it had no power to test.
