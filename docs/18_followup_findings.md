# Follow-up findings — after the hold-out closed

Run 2026-08-16, driven by operator questions while preparing the readout. Three blocks.
All reproducible: `scripts/followup_analyses.py` → `output/followup_analyses.txt`.

**Status of everything here: EXPLORATORY.** The pre-registered study ended when the 2026
hold-out was opened and scored (`docs/16`). Nothing below was predicted in advance, and
2026 is already spent — so where a 2026 number appears it is a *second look at used data*,
not validation. Any of these findings that we want to rely on needs fresh data
(Aug 2026 onward) or an A/B test.

---

## A. How outreach itself changed, 2025 → 2026

Structural, not about writing. Each send counted once (Apollo logs a Gmail twin; the
dedup in §9.9 applies).

| | 2025 | 2026 |
|---|---|---|
| Gmail hand-sent | 72.6% | **23.7%** |
| Apollo | 27.3% | 28.8% |
| Amplemarket | 0.1% | **47.5%** |

Per month, so the 12-vs-7-month windows are comparable:

| sends / month | 2025 | 2026 |
|---|---|---|
| Gmail hand-sent | 6,052 | 3,621 |
| Apollo | 2,278 | 4,389 |
| Amplemarket | 7 | 7,252 |
| **total** | **8,337** | **15,262** (1.83×) |

**Apollo was not replaced gradually — it collapsed in May–June 2026.** Monthly Apollo
sends: 6,717 (Mar) → 7,293 (Apr) → 4,122 (May) → **825 (Jun) → 809 (Jul)**, while
Amplemarket went 3,948 → 12,461 → 6,870 → 9,582 → **16,541**. Any annual average of 2026
hides this: the yearly figure says Apollo is 29% of sends, but by July it is 4%.
**July 2026 actual mix: 80% Amplemarket, 16% hand-sent, 4% Apollo.**

Cold-pitch writing, same population, outcome-blind:

| | 2025 | 2026 |
|---|---|---|
| templated (3+ identical) | 53.7% | 25.4% |
| visible mail-merge | 36.4% | 25.7% |
| **states a why-now** | **71.2%** | **54.0%** |
| question in subject | 19.4% | 6.1% |
| reuses name mid-body | 7.7% | 0.2% |
| under 100 words | 26.5% | 49.8% |
| median words | 112 | 101 |
| reply rate | 6.9% | 6.5% |

Reading: the mechanical habits improved (less templating, shorter, name-reuse gone) while
**the one confirmed positive lever went backwards** — 71% → 54% of cold pitches state a
reason to write now. Reply rate held roughly flat while total volume nearly doubled, which
means the scale-up did not dilute per-email quality in the channel we can measure. It says
nothing about Amplemarket, which is now most of the volume and has no reply attribution.

---

## B. Same-day send volume — a large new effect

A rep's reply rate falls sharply with how many first-touch emails they send that day.

**2025 cold pitches:**

| emails sent that day | n | reply rate |
|---|---|---|
| 1–2 | 481 | **16.4%** |
| 3–5 | 633 | 8.4% |
| 6–10 | 1,018 | 6.1% |
| 11–25 | 1,621 | 6.5% |
| 26+ | 1,400 | **4.0%** |

Within-sender, per doubling of same-day volume: **−1.67pp (p<0.0001)**.

**It is not the same thing as templating.** Both survive in one model:

| | 2025 | 2026 |
|---|---|---|
| templated | −4.14pp (p=0.0006) | −1.73pp (p=0.124) |
| volume, per doubling | −1.29pp (p<0.0001) | **−3.58pp (p<0.0001)** |

**The 2026 column is the uncomfortable one.** There, volume dominates and templating loses
significance. Two readings, and we cannot choose between them:

1. Volume is the more fundamental driver, and templating is partly a proxy for it — reps
   template *because* they are sending a lot.
2. 2026 simply has less data (n=1,286) and the templating estimate lost power; its sign is
   unchanged and its confirmed status rests on the pre-registered test in `docs/16`.

What this does **not** do is overturn the templating finding — that one was predicted in
advance and confirmed on sealed data. But it does mean **daily volume belongs next to it
in any recommendation**, and that a coaching intervention aimed only at prose may be
aiming at the smaller of the two levers.

**Selection caveat, stated plainly:** a rep sending 1–2 emails on a given day is probably
sending them *because* they had a specific reason for those two people. The comparison is
not "same rep, same intent, different volume" — it is "same rep, different kind of day."
Effect size is an upper bound.

---

## C. Why does templating cost 2–4×? Six probes, four dead ends

Recorded so nobody re-runs them.

| # | hypothesis | verdict |
|---|---|---|
| C1 | templates can't carry a why-now | **DEAD END** — 70.7% do, vs 71.8% hand-written. Identical. |
| C2 | the why-now inside a template is weaker, so works less | **DEAD END** — interaction p=0.216. The apparent +5.4 vs +2.6 gap is noise. |
| C3 | the text is simply worse | **PARTIAL** — controlling for all 19 measured text features moves the penalty only −5.40 → −3.95pp. **73% is not explained by anything we can measure in the writing.** |
| C4 | it scales with how many copies you send | **DEAD END** — flat. 2 copies (3.9%) is as bad as 25+ (5.6%); per-doubling p=0.33. A cliff, not a slope: the moment you reuse a body you pay full price. |
| C5 | spam filtering | **WEAK EVIDENCE AGAINST** — penalty by recipient company size: −4.75 (<200 emp), −5.09 (200–1999), −6.15 (2000+). Bigger firms have far stronger filters; the penalty barely moves. |
| C7 | most templates are dead, a few are great | **DEAD END** — 66% get zero replies vs 60% expected by chance; overdispersion only 1.29× (chi²=263, df=172, p=1e-5). Templates differ from each other, but modestly. Not a lottery. |

**C6 — the one positive clue. Reply latency.**

Among pushes that did get a human reply: templated **median 4.8 days** (n=134) vs
hand-written **1.8 days** (n=222).

If templates were being *blocked*, whoever received them would reply at normal speed. They
don't — they reply late. So the mail lands, is read, and is deprioritised. Most people
never come back to it (lower rate); the ones who do, come back late (slower). One
mechanism, two symptoms.

**Best-supported explanation:** recipients recognise mass mail and deprioritise it. The
recognition cue is not in our 12-quality rubric, which is why 73% of the penalty is
unexplained by measured text.

**Still unfalsifiable with this data:** within-rep targeting. A rep deciding *this account
gets a real email, that one gets the template* encodes account quality we cannot observe.
Only an experiment separates that from the text.

---

## D. The 2×2 worth keeping

Templating and why-now act independently; ~3× from worst corner to best.

| | has why-now | no why-now |
|---|---|---|
| **hand-written** | **10.7%** | 5.8% |
| **templated** | 5.4% | 3.6% |

---

## E. Two corrections made during this session

Both were claims I stated before testing them, then had to withdraw. Logged because the
pattern matters more than the instances.

1. **"The why-now works only half as well inside templates (+5.4 vs +2.6)."** Withdrawn —
   the interaction is p=0.216. Two separately-estimated numbers were read as a difference
   without testing the difference.
2. **"66% of templates get zero replies — they're all-or-nothing."** Withdrawn — 60% is
   what chance predicts at a 4.8% base rate on those sample sizes.

---

## F. Open items

- **Grade why-now 1–5** rather than yes/no (~$15 re-judge). Currently we can say a why-now
  helps, but not how much a *specific* occasion beats a generic one — which is exactly what
  a coaching tool would need, and exactly where Goodhart bites (templates already comply
  nominally 70% of the time).
- **Re-validate on Aug 2026+** as it accumulates. Same code, no new work. The volume effect
  and the directional findings would resolve.
- **A/B test** the two confirmed findings. The only way past the targeting confound.
- **Amplemarket reply attribution.** Without it, 80% of current sends are unmeasurable.
