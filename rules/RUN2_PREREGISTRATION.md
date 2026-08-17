# Run-2 pre-registration — outcomes, hypotheses, and bug protocol

Written **before** any Layer-1 or Layer-2 result is computed. Must be committed before the
first analysis command runs; the git timestamp is the evidence.

This document supersedes nothing in `rules/` — it adds the decisions that the first run
left open, and specifies the anti-defect protocol. Everything already pre-registered
(`eligibility_and_analysis_rules.md`, `analysis_splits_addendum.md`,
`reply_classifier_protocol.md`, `type_classifier_protocol.md`, `judge_rubric.md`) stands
unchanged.

---

## 1. Outcomes — Interested is CO-PRIMARY, not secondary

A reply is not the goal. 41% of human replies in this corpus carry no forward motion.

| Outcome | Definition | Status |
|---|---|---|
| `replied` | reply category = `human` | Co-primary |
| `interested` | `human` AND intent ∈ {`wants_call`, `asks_question`, `wants_materials`, `referral`} | **Co-primary** |

Rules, fixed here:

- **Every reported finding carries both numbers.** No claim may be stated on `replied` alone.
- Where the two disagree in direction, that disagreement is the finding and is reported as such.
- Where they agree, `interested` is the number quoted in the headline.
- `referral` stays inside Interested (pre-registered in `reply_classifier_protocol.md`).
  A sensitivity run excluding it is reported alongside.
- Observed baselines on the eligible corpus (n=14,769): replied 15.95% (2,355),
  interested 9.46% (1,397). Recorded here so a post-rebuild change is visible.

### 1b. Intent-label accuracy must be measured, not assumed

`replied` was verified at 99.0% two-pass agreement and gated at 90% before use.
`interested` was only spot-checked. Promoting it to co-primary requires the same standard.

**Gate: a 300-reply independent second pass, differently worded, measuring per-intent and
Interested-level agreement. If Interested-level agreement is below 90%, the intent
classifier is revised and re-measured before any Layer-2 analysis uses it.**

---

## 2. Pre-registered hypotheses — primary vs exploratory

All 12 rubric dimensions get scored. Only these four are **primary**; they are the only
ones eligible for a headline claim.

| # | Dimension | Direction predicted |
|---|---|---|
| 1 | `research_signal` | higher → more interested replies |
| 2 | `why_now` | present → more interested replies |
| 6 | `ask_clarity` | higher → more interested replies |
| 8 | `bespokeness` | higher → more interested replies |

Chosen because they are the dimensions that survived directionally in the prior SAO study
(personalization, why-now) plus the two the rubric-mining agents found most variable.

The remaining eight (`value_specificity`, `proof_relevance`, `pain_hypothesis`, `ask_size`,
`polish`, `economy`, `peer_tone`, `recipient_centricity`) are **exploratory**. Any finding
among them is labelled exploratory in the report and is never stated as a rule.

**Multiple-comparison rule, fixed now:** Benjamini–Hochberg across the 4 primary tests per
outcome. Exploratory dimensions are BH-corrected separately across all 8 and reported with
effect sizes and confidence intervals regardless of significance. No dimension is promoted
from exploratory to primary after seeing results.

---

## 3. Design — compare each rep against themselves

Primary specification is **within-sender**: sender fixed effects, cluster-robust standard
errors by sender. This asks whether a rep's own higher-scoring emails outperform their own
lower-scoring emails, which removes rep-level targeting skill from the comparison.

Reported alongside: the pooled (between-sender) estimate, so the gap between the two is
visible. Where they diverge materially, targeting confounding is the stated explanation.

Controls per `analysis_splits_addendum.md`, plus: `ca_class` (confirmed vs fallback),
year, opener type, and channel (mailbox vs sequencer).

Results are always reported split by `ca_class`, never pooled silently — the fallback-CA
inclusion doubles the corpus and remains the study's most consequential judgment call.

---

## 4. Is it 12 dimensions or one? — halo check, run before interpretation

If the judge is really scoring "is this a good email," the 12 dimensions collapse and we
have one finding, not twelve.

**Before any Layer-2 result is interpreted:** compute the 12×12 score correlation matrix
and the first principal component's share of variance.

- If mean pairwise |r| ≥ 0.6 **or** PC1 explains ≥ 50% of variance, the report leads with a
  single composite "craft" score and treats per-dimension claims as non-separable.
- The matrix is published in the report either way.

---

## 4b. Cross-model judge validation — two instruments, not one model twice

`judge_rubric.md` pre-registers a 10% re-score by a second pass of the **same** model. That
measures whether a model agrees with itself, which flatters it — every model is fairly
self-consistent. It stays (it is pre-registered), but it is the weaker check.

The stronger check, added here: **a 1,000-email overlap scored independently by a second,
more capable model.**

| | Model | Scope |
|---|---|---|
| Primary scoring | **Sonnet**, medium effort | all 14,769 openers |
| Same-model repeatability (per `judge_rubric.md`) | **Sonnet**, medium effort | random 10% |
| **Cross-model validation** | **Fable** | random 1,000 |

Rules, fixed here:

- **The overlap sample is drawn with a fixed seed, stratified by opener type × year only.**
  It is **not** stratified on `replied` or `interested` — the sample must not be
  outcome-aware.
- **Fable judges the overlap blind**, under the identical redacted prompt, with no sight of
  Sonnet's scores.
- **Sonnet's scores are the ones used in the analysis, for all 14,769 including the
  overlap.** Fable's overlap scores are used *only* to measure agreement. Mixing instruments
  inside the primary analysis would give 1,000 emails a different measuring device from the
  other 13,769.

### Agreement metrics and thresholds — set before the numbers exist

Per dimension: exact agreement, within-1 agreement, and quadratic-weighted kappa for the
1–5 scales; plain agreement for `why_now` (binary) and `ask_size` (categorical). Plus mean
signed difference, to detect one model scoring systematically harder than the other.

**A dimension passes if within-1 agreement ≥ 80% AND mean signed difference is within
±0.3 of zero.**

- **All dimensions pass** → Sonnet was sufficient; that is now a measured fact, reported.
- **A dimension fails** → it is re-scored on Fable for the **full** corpus, and only Fable's
  scores are used for that dimension. The failure and the re-run are reported.
- **More than half the dimensions fail** → the whole judging pass is re-run on Fable and the
  Sonnet pass is discarded. Reported in full.

Whatever the outcome, the per-dimension agreement table is published in the report.

---

## 5. Bug protocol — the part that matters most

The first run found five silent counter defects, each of which produced a believable wrong
number. Fixing them was not enough; nothing stops them being reintroduced. This section is
the defense.

### 5.1 Regression tests with the actual pathological inputs (NEW — build first)

`tests/test_features.py`, written and passing **before** the frame is rebuilt. One test per
known defect, each asserting the correct count on the real failing example:

| # | Defect | Test asserts |
|---|---|---|
| 1 | Tracking URL ending in `?` counted as a question | `n_questions == 0` on a body whose only `?` is in a `?utm_source=` URL |
| 2 | Unsubscribe / legal footer surviving signature split | footer text contributes 0 words and 0 questions |
| 3 | Hard-wrapped plaintext counted as sentences | a question wrapped across two lines yields 1 question, full text preserved |
| 4 | Signature logo / bold job title counted as body formatting | `has_bold == False`, `n_images == 0` when the only bold/image is in the signature |
| 5 | Short name/company matching common words | contact "Or" does not match the word "or"; company "Speak" does not match the verb |

Tests import and call the **production** functions in `scripts/features_compute.py` and
`scripts/text_clean.py` — never a re-implementation. (The first run's audit tool
re-derived text with its own regex and disagreed with what was actually stored.)

### 5.2 Placebo test — catches bugs in the analysis code itself (NEW)

Shuffle the outcome labels within stratum and re-run the complete Layer-1 and Layer-2
analysis unchanged.

**Any "significant" finding that survives on shuffled labels is a bug, not a result.**
Expected false-positive rate at α=0.05 is ~5%; materially more means the specification,
the clustering, or the join is wrong. Run before reading the real results, and report the
observed placebo rate in the methods appendix.

### 5.3 Per-batch coverage assertion — protects the outcome variable

9 of 209 batches in the first run silently returned 79 labels for 80 inputs. A missing
reply label makes an email look like "no reply", corrupting the outcome itself.

- Every batch validates returned IDs against input IDs.
- Gaps are re-run automatically, up to 3 attempts.
- Unresolvable gaps are a **hard failure**, listed by ID, never silently dropped.
- Agent self-reported counts are never trusted.

### 5.4 Blinding leak check — automated, before judges launch

Sender names leaked into ~30% of judge items in the first run via signature blocks the
sign-off detector missed. A judge that sees who wrote the email breaks the study's most
important rule.

Automated scan over every built batch for: sender local-parts across all four internal
domains (`encord.com`, `encord.ai`, `tryencord.com`, `cord.tech`), `@company` addresses,
raw URLs, ISO dates, and `wrote:`. **Non-zero hits block the launch.**

Over-redaction is equally damaging (an owner surnamed *Short* turned "a short call" into
"a [SENDER] call"). Redaction vocabulary is pruned by corpus frequency — any token
appearing in >2% of emails is dropped from the redaction list.

### 5.5 Join and row-count invariants — asserted, not eyeballed

At every merge, assert and log:

- `frame_G30` row count stays 15,586; only `replied` / `interested` / `type` fill rates change.
- No duplicate `email_id` in any label or score table.
- Label coverage % before and after, printed as a diff.
- Judge-score row count equals eligible-opener count exactly; any shortfall named.
- Totals reconcile across `reply_labels`, `type_labels`, `frame`, and judge scores.

Any assertion failure stops the pipeline. No stage proceeds on a warning.

### 5.6 Read the examples, on the production output

For every feature and every judged dimension: print 20 real examples spanning the score
range, and read them. This is what caught all five defects last time. It is not optional
and it is not replaceable by summary statistics.

### 5.7 Resumability and determinism

- One file per batch, skip-if-exists. Background runs die when the session is interrupted;
  recovery comes from the filesystem, not from agents.
- Fixed random seeds for every sample, shuffle, and split; seeds recorded in the output.
- Every number in the final report traceable to a named file in `output/`.

---

## 6. Execution order and models

No stage starts before the previous one's assertions pass.

| # | Stage | Model | Agents |
|---|---|---|---|
| 0 | Write regression tests (5.1); confirm they pass | Opus (direct) | none |
| 1 | Fill 116 reply + 434 type label gaps | **Fable** (matches the instrument that labelled the other 18,000) | ~14 |
| 2 | Intent-accuracy second pass, 300 replies (1b) | **Fable** | ~4 |
| 3 | Rebuild frame at G30 / G21 / G45; assert invariants (5.5) | Opus (direct) | none |
| 4 | Layer-1 analysis, both outcomes, within-sender | Opus (direct) | none |
| 5 | Placebo test on Layer-1 (5.2) | Opus (direct) | none |
| 6 | Build blinded judge batches; leak check (5.4) | Opus (direct) | none |
| 7 | Judge 14,769 openers × 12 dimensions | **Sonnet**, medium effort | ~370 |
| 8 | 10% same-model re-score (per `judge_rubric.md`) | **Sonnet**, medium effort | ~37 |
| 9 | Cross-model validation on 1,000-email overlap (4b) | **Fable** | ~25 |
| 10 | Agreement table; re-run any failing dimension on Fable (4b) | **Fable** if triggered | 0–370 |
| 11 | Halo check (4) | Opus (direct) | none |
| 12 | Layer-2 analysis + placebo repeat | Opus (direct) | none |
| 13 | Report: `output/REPORT.md` | Opus (direct) | none |

Agents are used **only** for classification and judging. Pulling, filtering, feature
computation, and analysis stay single-agent and sequential — parallel agents on the same
analysis files produce numbers that don't reconcile.

---

## 7. What this study will and will not be able to say

Stated now so it cannot be softened later.

**Can say:** how many follow-ups it takes before a reply comes; which countable email
properties are associated with human replies and with interested replies, within a rep's
own sending; whether the writing-quality dimensions are separable or one latent factor.

**Cannot say:** that any of it is causal. This is observational. A rep who personalises is
probably also better at choosing who to email, and no control in this design fully removes
that. Only a randomised send test settles causation, and that is a different project.

**Expected shape of the result:** one strong structural finding (the follow-up curve),
several countable associations, and a writing-quality layer that is directional at best.
The prior study's writing findings largely failed re-testing a year later; the same rubric
family carries the same risk.

---

## 8. Run configuration and provenance

### 8.1 Decision: continue the existing run, do not restart

Recorded with its reasoning, because the reasoning is the part that matters.

The expensive verified work exists (the pull, sender identification, reply labels at 99.0%
two-pass agreement, audited feature counters), and the git history is timestamped proof that
the analysis rules were fixed before any result was seen. A restart would destroy that proof
and re-register rules while already knowing what the data looks like.

The one thing a restart would buy — an independent second opinion — **is not available to
the agent running this study**, which has read `docs/LEARNINGS_FOR_NEXT_RUN.md`, the
methodology notes, and the contestable judgment calls. A nominally "fresh" run by this agent
would inherit those assumptions invisibly while appearing independent, which is worse than
continuing openly.

**Genuine replication is therefore a third run, later, by an agent that never sees this
repository — as validation, not as a restart.** That is what the prior SAO study did for its
own findings and it was the strongest thing in that project.

### 8.2 Inherited judgment calls, carried forward knowingly

Four decisions from run 1 are inherited rather than re-litigated. Each is stated in the
report; robustness runs exist where noted in `docs/LEARNINGS_FOR_NEXT_RUN.md` Part 4.

1. `G = 30` days as the push-boundary gap (robustness runs at 21 and 45 days).
2. `referral` counts as Interested (sensitivity run excluding it, per §1).
3. Including the 8,192 behaviourally-identified fallback CAs — roughly doubles the corpus
   and is the single most consequential decision in the study. Results always split by
   `ca_class`, never pooled silently.
4. Excluding `is_reply_like` openers (~4% of apparent cold pitches; 817 rows here).

### 8.3 Model provenance of the existing labels

The existing reply labels (16,695) and type labels (18,318) were produced on **Fable**.
This is recorded from the operator's own account of run 1, not recovered from run logs —
stated plainly so it can be challenged. It is the reason the 550 label gaps are filled on
Fable: they top up an in-progress instrument, and mixing models mid-classification would
mean some emails were sorted by one judge and some by another.

Outstanding gaps at time of writing: `data/missing_reply.txt` (116 ids),
`data/missing_type.txt` (434 ids).

### 8.4 Run configuration

| Setting | Value |
|---|---|
| Orchestrator model (Claude Code interface) | **Opus 5** |
| Orchestrator thinking | **high** |
| Ultracode | **off** — one workflow for the judging phase only; the analysis stages stay single-agent and sequential |
| Label-gap agents | Fable, default effort (matching the instrument) |
| Judging agents | Sonnet, medium effort |
| Cross-model validation agents | Fable |
| Approximate agent count | ~450 (≈370 judging, ≈37 re-score, ≈25 overlap, ≈18 labels) |

Ultracode is deliberately off: it would push a fan-out workflow onto the analysis stages,
which is the exact failure mode `docs/LEARNINGS_FOR_NEXT_RUN.md` Part 5 warns against.

### 8.5 Disclosure — what was known before this document was written

Stated so a sceptic does not have to find it.

Before the hypotheses in §2 were fixed, the following were already visible: the Q2
follow-up curve (`output/q2_curve_*.csv`), the overall reply rate (15.95%), the overall
interested rate (9.46%), and the 41% brush-off share of replies.

These are **marginal totals, not relationships between any email feature and any outcome**.
Knowing that 16% of recipients reply carries no information about whether naming a trigger
event helps. No feature-to-outcome result existed, and none exists now — zero emails have
been scored on the 12 dimensions.

What did inform the choice of the four primary hypotheses is the **prior SAO study's**
findings (personalization and why-now were the two that stayed directionally consistent
under blind validation). Prior-informed hypotheses are stronger than arbitrary ones; the
provenance is disclosed here so the choice can be judged independently.

### 8.6 Operator sign-off

Reviewed and confirmed by the operator before commit: `referral` remains inside Interested
(§1), and the four primary hypotheses in §2 stand as listed.

---

## 9. Corrections found at execution time (appended 2026-08-14, after GO)

§8.3 above is **wrong on the facts** and is left standing rather than edited, because
silently correcting a pre-registration destroys the thing it exists to provide. What
follows is the correction, with its own timestamp.

§8.3 recorded "116 reply ids" and "434 type ids" outstanding. Both numbers came from
`data/missing_reply.txt` and `data/missing_type.txt`, which turn out to contain **batch
names, not email ids**, and to be stale snapshots taken mid-run. The authoritative check is
the filesystem — per §5.7, recovery comes from the filesystem, not from a record of what
agents said they did.

### 9.1 Actual label state, measured from disk

| | batches | ids | labelled | missing |
|---|---|---|---|---|
| reply | 209 / 209 present | 16,695 | **16,695 (100%)** | 0 |
| type | 312 / 485 present | 38,793 | 24,960 (64.3%) | **13,833** |

Two consequences worth stating plainly:

- **No reply-label work was needed.** The reply outcome variable is complete, with zero
  partial batches — run 1's "9 of 209 batches returned 79 of 80 labels" defect is not
  present in the final state. §5.3's assertion is satisfied as found.
- **`data/type_labels.parquet` was itself stale** (18,318 rows against 24,960 labels
  present on disk). Re-running `scripts/assemble_labels.py` recovered 6,642 labels that
  had already been produced and paid for but never assembled.

### 9.2 The type gap is time-confounded, and that is the real problem

The 173 missing type batches are **contiguous: `batch_0312` through `batch_0484`**. Batches
were built in sorted-id order, and HubSpot engagement ids are near-monotonic in creation
time, so batch order is chronological. `batch_0312` lands at 2025-10; `batch_0484` at
2026-07.

The gap is therefore not a random 36% of the corpus. It is **the end of the time range**:

| frame | rows | type-null | of which 2025 | of which 2026 |
|---|---|---|---|---|
| G30 | 14,174 | 6,388 | 1,012 | **5,376 — every 2026 row** |

`build_frame.py` applies `is_reply_like.fillna(False)`, so an unlabelled opener is silently
assumed not-reply-like and kept. The `is_reply_like` safety net was therefore excluding
~11% of 2025 openers and **0% of 2026 openers**.

That is a differential exclusion sitting directly on the 2025-vs-2026 comparison — which is
the pre-registered holdout test (`eligibility_and_analysis_rules.md` §9). Pilot batches in
the missing window measured `is_reply_like` at 27–35% in cold-outreach batches, so the
excluded share was not small. Left unfixed, the holdout would have compared a
contamination-filtered development set against an unfiltered holdout, and any failure to
replicate would have been uninterpretable — on top of the channel-mix confound already
recorded in `docs/LEARNINGS_FOR_NEXT_RUN.md` Part 4.5.

**Action taken:** all 173 batches are labelled, not just the ~6,500 that fall inside a
frame. Trimming to frame rows would have typed the 2025 window corpus-wide and the 2026
window CA-only, reintroducing a 2025/2026 asymmetry of exactly the kind this correction
exists to remove. Instrument consistency across the time range is worth more than the
token saving.

### 9.3 Recorded baselines are superseded

§1 recorded `replied` 15.95% (2,355) and `interested` 9.46% (1,397) on n=14,769. Those were
computed with the stale type labels. After re-assembly and rebuild at G30 the eligible
frame is **14,174** rows (the reply-like exclusion rose from 817 to 1,412), with `replied`
15.3% and `interested` 9.0%. These will move once more when the 173 batches land, and the
final numbers are reported in the waterfall.

Both directions are downward and small, and neither is a feature-outcome relationship, so
this does not affect §2's hypotheses. The §8.5 disclosure logic applies unchanged.

**Final numbers, all 485 type batches landed (2026-08-14):** the correction is much larger
than the interim figures above suggested.

| | §1 as recorded | interim (stale types) | **final** |
|---|---|---|---|
| reply-like exclusion | 817 | 1,412 | **3,509** |
| eligible frame rows (G30) | 14,769 | 14,174 | **12,077** |
| of which 2026 | 5,376 | 5,376 | **3,486** |
| `replied` | 15.95% | 15.3% | **10.9%** |
| `interested` | 9.46% | 9.0% | **6.1%** |

**35% of the 2026 "cold openers" were not cold** — they were mid-conversation messages that
the thread check missed and the untyped safety net never caught. The pre-registered baseline
of 15.95% was inflated by roughly a third in relative terms, entirely by this contamination.

This is the single largest correction in the study, and it lands on the outcome variable's
denominator. It is also the clearest available evidence that the §9.2 defect was worth
finding: had the 2026 window stayed untyped, the holdout would have compared a 2025 cohort
with 11% of its contamination removed against a 2026 cohort with none of it removed.

These remain marginal totals, not feature-outcome relationships, so §2's hypotheses and the
§8.5 disclosure logic still stand unchanged. Every `type` × `year` cell is populated for the
first time; robustness at G21 and G45 moves in step (10.8% / 11.2% replied), so the
correction is not an artefact of the gap choice.

### 9.4 A sixth counter defect, found in the judge redaction path

`scripts/build_judge_batches.py` replaced the recipient's first name with `[NAME]` using a
bare substitution — no word boundary, minimum length 2 — and the company likewise at
minimum length 3. This is **the same defect as audit finding 5**, which was fixed on the
feature path and never fixed on the judge path: a recipient named "Al" turns "also" into
"[NAME]so", and a company called "Speak" turns "speaking" into "[COMPANY]ing".

It is the over-redaction half of §5.4, and it would have degraded exactly the dimensions
the study cares about — `polish`, `economy`, `bespokeness` — on an unknown subset of items.

Fixed before any batch was built (no scores existed, so nothing is invalidated): word
boundaries on both, and short single-word company names require the capitalised form,
mirroring the already-audited feature-path rule. Pinned by `tests/test_blinding.py`.

### 9.5 The seventh defect: addr-route replies credited to the wrong conversation

Found 2026-08-14, after §9.1–9.4, by the operator asking why a colleague-loop-in reply
was attached to a coffee invite.

**The defect.** Reply matching had two routes: `thread` (same thread id) and `addr` (any
inbound from the recipient within the window — the pre-registered fallback for
sequencer-era mail that carries no thread id, `eligibility_and_analysis_rules.md` §6).
The fallback was never verified. Audited: **thread-route replies were 100%
subject-consistent with their opener; addr-route replies only 27%.** 195 of 1,322
replied=True rows (14.8%) had a first candidate whose subject did not match the opener —
"Intro Alec & Ross" credited with a reply titled "Job in SF". Misattributions clustered on
heavily-touched contacts (median 6 touches vs 3), i.e. people with several conversations
running at once.

**The fix** (`build_pushes.py::subjects_match`, pinned by `tests/test_reply_matching.py`):
an addr-route candidate is kept only if its normalised subject matches the subject of any
outgoing touch in the push. Prefixes (Re:/Fwd:/Automatic reply:/Accepted:, DE/FR variants)
stripped; punctuation collapsed to tokens; equality or ≥6-char containment. The thread
route is untouched. Production writes its own audit trail (`data/addr_audit_G*.parquet`).

**Measured effect on the eligible frame (G30):** 3,182 addr-route decisions → 2,739 kept,
443 dropped. Dropped: 380 calendar_bot, 50 human, 8 out-of-office, 5 other. Outcomes:
replied 1,322 → 1,302 (10.9% → 10.8%), interested 736 → 721 (6.1% → 6.0%). G21 and G45
move identically (−0.2pp / −0.1pp).

The headline moves little because `replied` needs only one legitimate human candidate and
most contaminated pushes also had one; most dropped candidates were calendar bots that
never counted as human anyway. The real repair is **attribution**: which reply, which
intent, and `touches_before_reply` now come from a reply that is actually tied to the push.
The old matching injected other conversations' replies into exactly the per-email
comparisons this study exists to make.

**Direction of error, stated:** conservative. All 50 dropped human candidates were read
(§5.6). The large majority are plainly other conversations (other events, live-deal
traffic, other reps' threads). A minority — roughly a dozen — are debatable: the same
dinner under a renamed calendar subject, or "Encord <> Tier IV" answered under
"Encord x Tier IV | Catch-up". Those genuine replies are now missed, which understates
`replied` slightly. The alternative overstated it with unrelated conversations; for a
study whose question is "did THIS email get a reply", undercounting is the safer error.

**Knock-on:** the committed Q2 follow-up curve was computed on the old matching and must
be re-run before the report. The §9.3 baselines shift again, to 10.8% / 6.0% at G30.

### 9.6 What now exists that §5 only specified

| §5 requirement | Implementation |
|---|---|
| 5.1 regression tests, production functions, real pathological inputs | `tests/test_features.py` — 18 tests, all 5 defects, each paired with a positive control so the test cannot be satisfied by breaking the feature |
| 5.4 automated blinding leak check that blocks launch | `scripts/check_blinding.py` — exits non-zero on any hit; imports the production redaction vocabulary rather than re-deriving it; also reports the over-redaction direction |
| 1b intent-accuracy gate | `scripts/build_intent_accuracy_batches.py` (seed 20260814) + `scripts/intent_accuracy.py` |
| — | `tests/test_blinding.py` — 12 tests pinning both redaction directions |
| §9.5 fix | `tests/test_reply_matching.py` — 13 tests: real misattributed pairs rejected, genuine replies (incl. punctuation variants and replies to follow-up touches) still matched |

Total: 43 tests, passing.

---

### 9.7 Blinding defects found at judge-build time — the §5.4 gate was itself defective

Found 2026-08-15, **before any judging was paid for**, by executing the operator
instruction pinned in `RESUME.md`: *build the batches, run the checker, then print 20 real
judge items and read them with your own eyes.* The checker alone would not have been
enough — the most serious defect was in the checker.

Six defects, all in the redaction path, none of which changes any Layer-1 result:

| # | defect | measured impact before fix |
|---|---|---|
| D8 | `prune_common_words` used corpus frequency as a proxy for "ordinary English word" | **29.8% of judge items carried a sender name** |
| D9 | the subject line never had `EMAIL_RE` applied | 66 items shipped `sender@encord.com` in the subject |
| D10 | `split_signature` missed curly apostrophes, non-English sign-offs, and sign-offs with a trailing clause | full signature blocks (name + job title) survived |
| D11 | `check_blinding.py` pruned the vocabulary it was auditing | 4,543 leaking items reported **clean** |
| D12 | a bare domain typed as prose (`Encord.com`) has no scheme, so `URL_RE` missed it | 25 items |
| D13 | the recipient greeting kept a real first name when HubSpot held no `firstname`, or the rep used a nickname | 13.3% of items greeted a real person while 77% greeted `[NAME]` |

**D8 is the one that matters, and it is a lesson about proxies.** The run-1 leak was
sender names surviving in signatures; §5.4 was written to stop it. The fix redacted every
name token, which over-redacted ordinary words (an owner surnamed *Short* turned "a short
call" into "a [SENDER] call"), so a pruning rule was added: a token appearing in more than
2% of emails is vocabulary, not identity. That reasoning inverts exactly where it matters —
**a prolific rep's name is frequent because they are prolific.** It pruned `decaudaveine`,
`fourati`, `kirpalani`, `landau`, `hansen`, `sweeney` and `ulrik` (13.2% of items). The
result was a 29.8% leak rate: the run-1 number, reproduced by the fix written to prevent it.

The replacement asks a question frequency cannot answer: **does the token ever appear
lowercase?** Ordinary words do, constantly; names do not. It is evaluated on the text as
the judge will see it — signature stripped, addresses and URLs removed — because two
earlier attempts were evaluated on the wrong string and each let a name through
(`james.sweeney@encord.com` made `james` and `sweeney` look like words; a lowercase handle
inside a to-be-stripped signature did the same for `zainab`).

**D11 is the structural lesson and is why the gate must never be trusted alone.** The
checker called `prune_common_words()` and then searched only for the tokens that survived
pruning. Any token the builder wrongly classified as an ordinary word was, by construction,
a token the checker would not look for. **An audit that inherits the assumption it is
auditing cannot fail.** This is the same defect class as §9.4 and as
`docs/LEARNINGS_FOR_NEXT_RUN.md` #12. The checker now searches the full unpruned
vocabulary and reports the pruning decision as a separate reviewable list.

Result after fixes: **0 leaks across 12,462 items, all six checks at zero, exit 0.**
The pruned-as-ordinary list is now `billing, growth, hello, jan, kit, marketing, max, near,
ray, short, team, will` — every entry an ordinary word or a calendar term, reviewed by eye.
Two knowingly accepted residuals: `max` (72 items) and `kit` (4) are genuinely ambiguous,
and redacting them would damage prose the judge must rate.

The counting splitter `split_signature()` was **deliberately left untouched** — feature
counts and the committed Layer-1 results depend on it. The judge path uses a separate,
stricter `split_signature_strict()`, pinned by a test asserting the counting variant has
not moved.

Tests: `tests/test_judge_redaction_v2.py` — 18 tests, one per defect plus positive
controls. Suite total **61, passing**. Test D9 caught a real ordering bug while being
written: bare-domain redaction ran before address redaction, so the domain half of
`james.sweeney@encord.com` became `[LINK]`, `EMAIL_RE` then failed to match, and the local
part — the sender's name — survived.

### 9.8 Judge corpus tied to the analysis frame

Selecting the judge corpus straight from `pushes_G30` swept in openers no frame contains:
replies inside an existing thread ("Re: Techex Expo" → *"Assume you're busy with the
presentation?"*) and one triathlon training plan. **3,183 of 15,173 items (21%) could never
enter any analysis and would have been paid for.** In the other direction, 487 rows that
are in a frame had no judge coverage, which would have left the pre-registered G21/G45
robustness runs with holes.

The corpus is now the union of the G21/G30/G45 frames: **12,462 items, 312 batches**, 0
outside any frame, 100.0% coverage of G30 `cold_pitch` + `event_invite`. Judging remains
independent of the **type** classifier — types are not consulted — so the two blind passes
still do not depend on each other. Frame membership is decided by eligibility, never by
outcome, so blinding is unaffected. This supersedes the "14,769 openers" figure in §6
stage 7; it is an efficiency change that cannot alter a result, and it removed every
over-redacted item (items >15% placeholder tokens: 21 → **0**).

### 9.9 What "mailbox" actually means — Apollo IS in the study

Established 2026-08-15, after the operator challenged the claim that sequencer mail was
excluded. **The channel label does not mean what its name suggests, and two statements
made earlier in this run were wrong.**

`build_timeline.py` sets `channel = mailbox` when HubSpot's `source == "EMAIL"` (a Gmail
sync record) and `sequencer` when `source == "INTEGRATION"` (a tool's own log). It then
de-duplicates across routes and, on a tie, **keeps the mailbox record** (`ch_rank`
mailbox=0 < sequencer=1).

Apollo sends *through* Gmail. So an Apollo email produces **both** records, the dedup
keeps the Gmail one, and it enters the study labelled `mailbox`. Amplemarket does not
leave a matching Gmail record (62,237 sends in 2026, only 430 with a Gmail twin), so it
stays `sequencer` and is excluded.

**Therefore: Apollo is included, Amplemarket is almost entirely excluded, and this was
true in both years.** The rule never changed; only the mix did.

| study population (frame openers) | 2025 | 2026 |
|---|---|---|
| also logged by a tool | **15.6%** | **53.6%** |
| cold pitches, tool-logged | 16.5% | 43.6% |
| tools present | Apollo 1,344 | Apollo 1,712, Amplemarket 155 |

Two corrections to the record. (a) "We never counted Apollo" — **wrong**; 16.5% of 2025
cold pitches are Apollo. (b) "2026's Gmail slice is the hand-written residue" —
**wrong, and backwards**: the tool-logged share of the study population more than
tripled. Apollo volume rose (27,150 → 45,859 sends); it was never replaced, Amplemarket
was added on top.

**Does the mix shift distort the study? Tested, and no.**

1. *Level.* Tool-sent openers reply **1.9pp lower** after features and sender FE
   (p=0.018). Reply-matching composition is near-identical by route (76% vs 81% matched
   by thread), which argues against a large attribution gap, but genuine
   worse-performance and residual under-capture cannot be fully separated. Reported as a
   limitation.
2. *Slope — the one that matters.* Every headline feature keeps its sign in **both**
   routes: templated −5.8 / −5.4, short ≤100 +4.5 / +5.2, subject-question +4.6 / +3.8,
   2+ questions −2.3 / −3.7, why_now +5.1 / +2.4, recipient-centricity +6.6 / +0.6
   (hand / tool). Formal interaction tests find no difference: templated p=0.757, short
   p=0.582, why_now p=0.178. The only sign flip, `has bold`, has p=0.65 on the tool arm
   — noise, not a flip.

So the reweighting hazard — that a 2026 prediction could fail purely because the
hand/tool blend changed — is **not supported by the data**. The findings are properties
of the email, not of the send route.

Implemented: `data/tool_flag.parquet`; `analyze_q1.py --tool {hand,tool}` and
`--control-tool`. The control is **off by default** so the committed 2025 estimates stay
reproducible; with it on, no headline effect moves by more than 0.1pp.

**Known scope leak, documented not hidden:** 155 Amplemarket openers (65 of them 2026
cold pitches, ~5% of that cell) are inside the study because they did leave a Gmail
twin. The stated rule excludes Amplemarket. They are left in place — removing them
post-hoc, after their existence was discovered, is the kind of after-the-fact filtering
this pre-registration exists to prevent — and every 2026 test is additionally reported
with `--tool hand`, which excludes them entirely.

### 9.10 The blinding gate's verdict depends on corpus size — found 2026-08-17

Found while building the graded why-now pass (`rules/judge_rubric.md` addendum). The item
texts handed to that pass are copied **byte-for-byte** out of `output/judge_batches/`,
programmatically verified identical (`scripts/build_whynow_batches.py::verify_verbatim`).
The same texts produce two different gate verdicts:

| corpus handed to `check_blinding.py` | items | verdict |
|---|---|---|
| `output/judge_batches` (full) | 12,462 | **CLEAN — 0 leaks** |
| the cold-pitch subset of exactly those items | 7,055 | **BLOCKED — 14 hits** |

**Cause.** `prune_common_words` decides whether a name token is really an ordinary English
word from *lowercase evidence inside the corpus it is given* (§9.7). `max` and `kit` clear
that threshold at 12,462 items and fall below it at 7,055, so on the subset they revert to
being treated as sender vocabulary. The thresholds are relative; the verdict therefore is.

**The 14 hits are not leaks.** Every occurrence was read. All are third parties named in
body text, none an Encord sender: Max Stratmann and Max Gariel (people a rep met at
events), Max Romero of Overland AI (a named peer), **Max Curie of IAS's data science
team — the recipient's own colleague**, the Max Planck Institute (twice, misspelled
"Plank"), and a Max who worked at Samsara. Redacting these would be over-redaction of the
worst kind for this particular pass: a named referral is exactly the grade-4/5 evidence
the why-now scale is built to detect.

**Nothing was hidden by the original run.** `max` and `kit` appear by name in that run's
PRUNED-AS-ORDINARY list, which §9.7 made a separate reviewable output precisely so a
pruning decision could never pass as an absence of leaks. The structural fix worked: this
was resolved by reading the list, in minutes.

**Decision for this run.** The gate is run on the full corpus, which is where the pruning
list was reviewed and signed off, and the guarantee for the subset is the byte-identity
check rather than a re-derivation. Re-deriving redaction for a subset would mean a second
implementation of the thing that leaked in run 1 — the mistake `check_blinding.py`'s own
docstring records. Pinned by `tests/test_whynow_batches.py`.

**Not fixed in code, deliberately.** Making the gate take its vocabulary decision from a
reference corpus while checking a subset is the right fix, but changing a launch-blocking
gate in the middle of a spend is how gates stop meaning anything. Logged for the next run;
`docs/LEARNINGS_FOR_NEXT_RUN.md` carries it.
