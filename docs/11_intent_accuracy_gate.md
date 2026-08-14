# The §1b gate on `interested` — FAILED at 83.3%, and exactly why

Run 2026-08-14. Pre-registered in `rules/RUN2_PREREGISTRATION.md` §1b:

> Gate: a 300-reply independent second pass, differently worded, measuring per-intent and
> Interested-level agreement. **If Interested-level agreement is below 90%, the intent
> classifier is revised and re-measured before any Layer-2 analysis uses it.**

## Method

Same shape as the check that validated `replied` at 99.0% (`docs/08`): pass B is asked a
**different question**, never shown pass A's taxonomy, and the label is derived
mechanically afterwards in `scripts/intent_accuracy.py`.

- Pass A (production): "assign one of 9 intents."
- Pass B: "say in one sentence what the writer is asking for; is there a concrete next step
  the recipient can now take; pick one of 10 forward-motion categories." Pass B was
  explicitly told **not** to consider whether the reply was good news.
- Sample: 300 random pass-A `human` replies, seed 20260814, plus a 150 booster for the thin
  intents (never pooled into the gate). Model: Fable, matching the instrument.

## Result: FAIL

| | agreement |
|---|---|
| **Interested, pre-registered definition (the gate)** | **83.3%** (249/299) |
| Interested excluding `referral` (§1 sensitivity) | 82.8% (236/285) |
| Pass-B `next_step` boolean alone (secondary) | 76.3% (228/299) |

Base rates: pass A calls 46.2% of human replies interested; pass B calls 61.5%. Pass B is
systematically more generous — this is a directional disagreement, not noise.

## The failure is one bucket, and it is the catch-all

| pass-A intent | n | same Interested side |
|---|---|---|
| `wants_materials` | 63 | 100.0% |
| `wants_call` | 80 | 98.8% |
| `asks_question` | 81 | 97.5% |
| `referral` | 64 | 95.3% |
| `not_interested` | 21 | 90.5% |
| `not_now` | 24 | 87.5% |
| **`other_human`** | **116** | **62.9%** |

**All eight real intents combined agree at 96.2% (176/183).** `other_human` — 39% of the
sample — agrees at 62.9%. Resolve `other_human` perfectly and the gate reads 97.7%.

So this is not a classifier that mislabels intents. It is a **catch-all bucket whose
boundary is undefined**, and two competent readers split it differently.

What pass B calls the 116 `other_human` replies:

| pass B | n | B calls it interested? |
|---|---|---|
| `acknowledges_only` | 44 | no |
| `none_of_these` | 20 | no |
| `proposes_or_accepts_meeting` | 16 | **yes** |
| `asks_for_information` | 11 | **yes** |
| `requests_document_or_demo` | 11 | **yes** |
| `redirects_to_colleague` | 5 | **yes** |
| `declines` | 5 | no |
| `defers_to_later` | 4 | no |

43 of 116 (37%) of `other_human` are read by pass B as forward motion.

## A hypothesis that was tested and rejected

The sample was drawn from all 10,957 human replies, but `interested` is only ever computed
from replies attached to an eligible push. Many of the disagreements are visibly mid-funnel
traffic — a signed NDA, a POC data handover, "add Ravi to the invite" — so the obvious
hypothesis was that the failure is an artefact of scoring replies the study never uses.

**It is not.** Restricting to frame-linked replies:

| population | n | agreement |
|---|---|---|
| frame-linked (the population `interested` is computed on) | 128 | **83.6%** |
| not frame-linked (never enters the study) | 171 | 83.0% |

Identical. The gate fails on the population that matters. Recorded because it would have
been an easy and wrong way out.

## Which pass is right? Genuinely mixed — read these

Pass B is **not** ground truth, and at least one disagreement is clearly pass B's error:

- *"This dinner is in London? I'll be in the states those days so can't make it but I
  appreciate the invite!"* — A: `not_interested`. B: `asks_for_information`. **A is right**;
  B keyed on the question mark inside a decline.

But some look like genuine misses by pass A:

- *"Please add Ravi Lambi (rlambi@dori.ai) to the invite as well."* — A: `other_human`.
  B: `redirects_to_colleague`. **B is arguably right** — looping in a colleague is forward
  motion, and it is close to the pre-registered `referral`.
- 16 replies A filed as `other_human` are read by B as proposing or accepting a meeting. If
  that is right, `interested` is **under**-counted, which matters more than over-counting:
  it would shrink the outcome and bias every effect toward zero.

## What happens next — and what must not happen

Per §1b the classifier is revised and re-measured. Two guard rails on that:

1. **Do not tune pass A until it agrees with pass B.** Pass B has its own errors
   (above). Agreement with a second imperfect instrument is not accuracy.
2. **Do not redefine `interested` to make the gate pass.** That is fitting the outcome
   definition to the measurement, and the definition is pre-registered.

The defensible sequence:

1. **Adjudicate first, re-label second.** Take the 116 `other_human` replies and resolve
   them under a *sharpened written definition* of the `other_human` / forward-motion
   boundary, before touching the other 10,841. The whole gap lives here; re-labelling
   everything without knowing which pass is wrong would be expensive and uninformative.
2. Sharpen the boundary in `rules/reply_classifier_protocol.md` as an appended addendum
   (never an edit — same rule as §9), stating what does and does not count as forward
   motion for the cases actually observed: an intro/loop-in, a POC or contract-execution
   step, a question inside a decline, a bare acknowledgement.
3. Re-label the `human` replies under the sharpened definition (~137 batches, Fable).
4. Re-run this gate on a **fresh sample with a new seed** — re-measuring on the same 300
   would be measuring the tuning, not the classifier.

## Status of the study while this is open

- `replied` is unaffected: 99.0%, validated in `docs/08`, still the solid outcome.
- **Layer-2 judging is blocked from using `interested`** until the gate passes. This is the
  pre-registered consequence and it is being honoured.
- Layer-1 on `replied` is not blocked by §1b, but §1 requires every finding to carry both
  numbers, so nothing is reported on either outcome until this resolves.
- Nothing has been judged. Zero scores exist. No result has been looked at.

Reproduce: `.venv/bin/python scripts/intent_accuracy.py`
Artefacts: `output/intent_accuracy/intent_agreement.csv`, `gate_result.json`,
`sample_manifest.json` (seed 20260814).

---

# Resolution (2026-08-14, same day)

## What was done

Per §1b's pre-registered consequence — "the intent classifier is revised and re-measured".

**1. The boundary was written down.** Five operator rulings appended to
`rules/reply_classifier_protocol.md` (appended, never edited). The fifth was added only
after the model test below exposed a shape the first four did not cover.

**2. Model choice was measured, not asserted.** 5 batches (400 replies) labelled by BOTH
Fable and Sonnet under the four rulings:

| | |
|---|---|
| Interested-level agreement | **87.8%** |
| Fable says interested | 56.8% |
| Sonnet says interested | 57.5% |

No capability gap. Decisive evidence came from the `evidence` field, which forces each
agent to quote the words that decided it: **both models repeatedly quoted the SAME words
and disagreed** — *"That would be great, thank you!"*, *"Looking forward to chatting!"*,
*"see you then"*. 29 of 49 disagreements were one shape: **committing to a meeting that was
arranged earlier.** The rulings had no rule for it, and neither model had a stable one.
Hence **Ruling 5 (commitment vs acknowledgement)**, and Sonnet for the relabel.

**3. Scope was cut by an order of magnitude, on the operator's insight.** Asked why
"looking forward to it" was even being argued about — it implies acceptance already
happened, so it is a later message in a conversation already counted. Measured: the 49
disagreements changed the outcome of **2 of 12,077 pushes (0.02%)**, because `interested`
is an OR across all of a push's replies and an earlier reply had already set it.

Consequence: the relabel targets only `other_human` replies **attached to a study push** —
677, not 4,030. 8 Sonnet batches, ~$7, against the $85 originally planned.

## The result

Of the study-linked `other_human` bucket, **62.3% was not "other" at all**:

| pass A | after relabel | change |
|---|---|---|
| `wants_call` 3,476 | 3,749 | **+273** |
| `wants_materials` 402 | 469 | +67 |
| `referral` 371 | 423 | +52 |
| `asks_question` 1,091 | 1,141 | +50 |
| `not_interested` / `not_now` | | +34 |
| `other_human` 4,030 | 3,554 | **−476** |

Interested replies 5,340 → 5,782. **Push-level `interested` 6.0% → 6.9%** (G21 6.7%,
G45 7.2%). `replied` is unchanged — the category layer was not touched.

`interested` was **under**-counted, the worse direction: it biases every effect toward zero
and would have produced "nothing works" conclusions from a real signal.

## The check that makes it credible

A one-directional correction is not evidence. Only the bucket believed to be broken was
re-examined, which is a biased search — you find what you go looking for.

So: **240 replies already labelled interested** (seed 99, study-linked) were re-read blind
under the same rulings, by the same model, with no indication of their existing label.

| | |
|---|---|
| stayed interested | **97.5%** (234/240) |
| moved out | **2.5%** (6) |

Against 62.3% moving in on the forward pass: a **25:1 asymmetry**. A generous model would
move replies in both directions; this one moves them in one. The correction is real.

All 6 movers are a single coherent pattern — *"I won't be at CVPR, but some colleagues may
be"* — a decline with an unnamed redirect, correctly moved out of `referral`, which
requires a **named** person.

The reverse sample is a **validation and is not applied**. Applying a re-read of 240 of
1,359 interested replies would leave that bucket inconsistently labelled — the exact defect
this exercise removes.

## Honest residuals

- **The pre-registered gate number stands as failed: 83.3% at reply level.** It is not
  deleted, replaced, or re-scoped. The push-level number is reported *alongside* it, with
  the reason: `interested` is a per-push OR, so reply-level disagreement overstates
  outcome-level disagreement. Changing what you measure after it fails is the move
  pre-registration exists to prevent, so both numbers go in the report.
- **~2.5% of the already-interested labels are known-imperfect** and left in place, for
  consistency. Measured, not estimated.
- **Non-study `other_human` replies (3,353) keep their pass-A label.** They feed no
  outcome. Anyone re-framing the corpus (different G, different CA rule) must relabel them
  before use.
- **One shape still unruled:** answering event logistics (dietary needs, plus-ones) without
  an explicit commitment phrase. 28 replies, currently split 18 interested / 6 not.
  Immaterial, but undecided.
