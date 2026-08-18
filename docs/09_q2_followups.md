# Question 2 — how many follow-ups were needed

Population: 15,586 eligible pushes (CA-sent, mailbox-opened, Jan 2025 – Jul 2026).
Script: `scripts/analyze_q2.py`. Outputs: `output/q2_curve_*.csv`.

## The curve (conditional, the honest construction)

Of the people who had **not** replied when touch *n* went out, what share replied to it:

| touch | people who got it | replied after it | reply rate | range | left because the rep stopped |
|---|---|---|---|---|---|
| 1 | 15,586 | 1,448 | **9.3%** | 8.8–9.8% | — |
| 2 | 10,202 | 820 | **8.0%** | 7.5–8.6% | 3,936 |
| 3 | 5,176 | 270 | **5.2%** | 4.6–5.9% | 4,206 |
| 4 | 2,007 | 84 | **4.2%** | 3.4–5.2% | 2,899 |
| 5 | 1,081 | 53 | 4.9% | 3.8–6.4% | 842 |
| 6 | 543 | 24 | 4.4% | 3.0–6.5% | 485 |
| 7 | 286 | 12 | 4.2% | 2.4–7.2% | 233 |
| 8 | 189 | 6 | 3.2% | 1.5–6.8% | 85 |

**Cumulative share of all pushes that got a human reply**: 9.3% after email 1 → **14.6%
after email 2** → 16.3% after 3 → 16.8% after 4 → 17.2% after 5 → 17.4% after 8.

Reading it plainly: the second email is worth nearly as much as the first (it lifts the
total from 9.3% to 14.6% — over a third of all replies arrive after email 2). The third
adds about 1.7 points. From the fourth onward each email adds well under a point.

## Robustness

Recomputed on the 14,514 pushes where **every** touch was a rep-mailbox send (so no reply
can be hidden by sequencer invisibility): 9.3% → 8.0% → 5.0% → 4.4%, cumulative 16.8%.
Materially identical, so trap 1 does not distort this answer.

## How much chasing actually happens

Touches per push: median 2, mean 2.8. 28% of pushes are a single email with no follow-up
at all; 20% get four or more.

## The caveat that cannot be fixed (pre-registered, stated in the report)

The "left because the rep stopped" column is the whole problem: 3,936 people never
received a second email, 4,206 more never received a third. Reps stop when they judge an
account dead — so the people who *keep* getting emails are the ones reps chose to keep
chasing. This curve therefore **cannot** separate "the extra email worked" from "reps kept
chasing the promising ones". It is reported as **suggestive only**.

It does, however, avoid the worse error the brief warns about: it never compares people
who received 5 emails against people who received 2. Each row asks only "among people who
were still silent and did get this touch, how many replied to it".

Email touches only — calls, LinkedIn and any other channel are not counted, so this is not
a total-contact count.

---

## Addendum 2026-08-18 — attacking the selection, and failing to beat it

Operator asked whether we can properly tell reps to keep emailing past 3, or to stop.
`scripts/followup_persistence.py` → `output/followup_persistence.txt`. EXPLORATORY.

**Design.** Reps differ in persistence, and persistence is closer to a habit than a
per-account judgement. For a rep who continues with almost every silent prospect, the 4th
touch is nearly unselected, so their touch-4 reply rate approximates what a 4th email does
for an ordinary prospect rather than a hand-picked one.

**How selective the stop decision is,** of prospects still silent after touch *n*:

| after touch | continued to the next |
|---|---|
| 1 | 74.7% (8,604 / 11,522) |
| 2 | 56.4% (4,600 / 8,151) |
| **3** | **38.1% (1,687 / 4,427)** |
| 4 | 54.0% |
| 5 | 53.4% |

The 3→4 decision is the most selective in the whole sequence. The 1→2 decision is barely
selective at all, which matters below.

**Reply rate to touch 4, by how selective the sending rep is** (16 reps with ≥30 silent
prospects after touch 3; continuation ranges 6% to 82%):

| sending rep | touch-4 reply rate | 95% CI |
|---|---|---|
| picks carefully (<35% continued) | 6.3% (10/158) | 3.5–11.3% |
| middling (35–65%) | 2.7% (34/1,277) | 1.9–3.7% |
| **chases nearly everyone (>65%)** | **2.9% (4/136)** | **1.1–7.3%** |
| *pooled, from the curve above* | *4.2%* | — |

Touch 5 repeats the pattern (15.0% on 3/20, 3.5%, 3.6%).

**Reading, honestly.** The direction says selection *is* doing work — careful pickers get
roughly double what indiscriminate chasers get, and the near-unselected estimate for a 4th
email is ~3% rather than the pooled 4.2%. But it rests on 4 replies out of 136 with a CI
from 1.1% to 7.3%, so it cannot carry a recommendation either way.

**Rep-level policy check — uninformative.** Across 22 reps with ≥100 prospects:
corr(share of prospects reaching email 4+, overall reply rate) = **+0.229**, while
corr(mean touches per prospect, overall reply rate) = **−0.229**. Two measures of the same
construct with opposite signs on 22 units is noise, not evidence.

**Verdict.** The pre-registered position stands unchanged: **the curve cannot tell us where
to stop.** One claim made verbally during the readout — that reps stop well before
follow-ups stop paying — is **withdrawn**; this cut points weakly the other way.

**What does survive.** The 1→2 decision is only 25% selective, so the second email's 8.0%
is close to unselected and the recommendation to always send it is safe. Everything from the
4th on needs the experiment: assign sequence length rather than let reps choose.

---

## Addendum 2 — 2026-08-18, the Apollo cut: the selection bracketed at last

Operator asked for it after the persistence cut failed to settle touch-4 value.
`scripts/followup_apollo.py` → `output/followup_apollo.txt`. EXPLORATORY.

**Design.** Apollo follow-ups fire from a sequence template — the judgement happens once,
at enrollment, not per-prospect per-touch. If Apollo pushes continue with silent prospects
at ~90%+, their curve is nearly unselected and touch-4's true value reads off directly.

**The premise half-failed, reported first:** Apollo continuation among still-silent is
48.7% after touch 2 and 30.1% after touch 3 — the same range as hand-followed pushes
(52.3% / 33.0%). Sequences end, or reps pull people. Apollo is NOT autopilot in this data,
so this is a weaker-selection view, not a no-selection one.

**Curves by follow-up route** (touch-1 rows are biased down by construction — a push is
only classifiable when follow-ups exist, which drops quick repliers — read from touch 2):

| touch | Apollo-sequenced (2,012 pushes) | hand-followed (5,977) |
|---|---|---|
| 2 | 4.5% (86/1,921) | 5.5% (314/5,713) |
| 3 | 3.2% (29/894) | 3.9% (111/2,826) |
| 4 | **1.2% (3/260)** | 2.9% (26/895) |
| 5 | 1.9% (2/105) | 4.3% (18/421) |
| 7 | — | **7.7% (7/91)** |

The hand tail RISES to 7.7% at touch 7 — the signature of reps chasing the prospects they
believe in. The Apollo curve, where per-touch choosing is weakest, falls monotonically.

**Three views of touch 4 now agree in ordering:** pooled curve 4.2% (most selected) >
chases-everyone reps 2.9% > Apollo sequences 1.2% (least selected). The more selection is
removed, the lower the number. The pooled 4%+ tail is therefore selection-inflated, and
the honest value of a 4th email is **~1–3%** — bracketed, since Apollo enrollment may
itself skew cold (a floor) while hand-followed skews warm (a ceiling).

**What strengthens:** the second email holds everywhere — 4.5% inside sequences where
nobody chose to send it, ≈ the opener's rate. "Always send the 2nd" no longer rests on the
low-selection argument alone.

**Verdict, superseding Addendum 1's "cannot say":** diminishing returns are real and start
after email 3. Emails 1–3 carry the value; a 4th is a 1–3% shot. Still exploratory — the
assigned-length A/B remains the only clean answer — but the direction is no longer open.
