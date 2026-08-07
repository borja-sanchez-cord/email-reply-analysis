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
