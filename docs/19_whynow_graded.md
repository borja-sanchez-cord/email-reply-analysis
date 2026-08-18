# Graded why-now (0–5) — the open item from `docs/18` §F, closed

Run 2026-08-17 on the operator's instruction. 6,415 cold-pitch openers graded 0–5 on a
single question — how specific and checkable is the stated occasion for writing now — plus
a 640-item independent second pass for reliability. 177 Sonnet agents, ~$16.

**Everything below is EXPLORATORY.** The 2026 hold-out was opened on 2026-08-15
(`docs/16`) and is spent. The 2026 column is a second look at used data. Nothing here
confirms, strengthens or weakens the pre-registered binary `why_now` finding, which stands
on its own pre-registered test.

Reproducible: `build_whynow_batches.py` → the graded pass → `assemble_whynow_grade.py` →
`whynow_agreement.py` → `whynow_grade_analysis.py`.

---

## 0. What was fixed in advance, and why it matters here

The operator named the exact trap before any money was spent: run the pass, see an
interesting effect, *then* decide the reliability was good enough. So the threshold was
fixed first.

Committed at `041ee6c`, **before a single email was graded**: the 0–5 anchors, the primary
contrast (top-2-box 4–5 vs 1–3, restricted to grade ≥ 1), and the gate — Cohen's kappa on
that same split, **≥ 0.50 usable, < 0.50 binned and the failure written up**. The gate is
enforced structurally, not by promise: `whynow_grade_analysis.py` recomputes kappa and
refuses to estimate anything below threshold, and neither the assembly nor the agreement
script opens the frame, so the gate is evaluable before any outcome is visible.

Prior expectation, recorded at the time: roughly even odds of clearing 0.50, because every
1–5 dimension already graded came back shakier than its binary counterpart. That
expectation was wrong in the study's favour.

---

## 1. The gate — PASSED, and this is now the most reliable judgment in the study

| | kappa | raw agreement |
|---|---|---|
| **`why_now_grade` 4–5 vs 1–3 (the gate)** | **0.780** | 89.0% |
| 4–5 vs 0–3, unconditioned | 0.790 | 89.5% |
| 0 vs ≥1 (does an occasion exist at all) | 0.587 | 96.7% |
| — binary `why_now`, for comparison | 0.716 | 90.9% |
| — `research_signal`, best of the 1–5 dimensions | 0.749 | 88.0% |

Exact-grade match 67.6%, within-one 87.2%, mean 3.07 vs 3.03 across the two runs.

Asking **one** question with six written anchors produced a more repeatable judgment than
asking twelve questions at once — including a more repeatable judgment than the *binary*
version of the same question. That is worth carrying into any future judging design.

The grade distribution helps: mass sits away from the 3/4 boundary that decides the split
(only 6.7% land on grade 3), and the split itself is near-even at 52% / 48%, which is the
best case for both power and kappa.

---

## 2. The result — a clean monotone gradient, 3.5× end to end

2025 cold pitches, human reply rate by grade:

| grade | what it means | n | reply rate |
|---|---|---|---|
| 0 | no occasion at all | 100 | 3.0% |
| 1 | sender-side ("we just raised", "we onboarded X") | 760 | 3.9% |
| 2 | a real event, offered to a list (dinner, booth) | 1,301 | 4.5% |
| 3 | tied to their category, not to them | 348 | 4.9% |
| 4 | tied to **this recipient**, checkable | 1,799 | 7.4% |
| 5 | the same, and it **drives the ask** | 845 | **13.5%** |

Monotone across all six levels. **Grade 5 replies at 3.5× grade 1** — 13.5% vs 3.9%.

Primary contrast, sender fixed effects, SEs clustered on sender:

| | 2025 (training) | 2026 (spent hold-out) |
|---|---|---|
| replied | **+4.43pp** (SE 0.94, p<0.0001) | **+3.94pp** (SE 1.14, p=0.0006) |
| interested | **+3.59pp** (SE 0.67, p<0.0001) | **+3.42pp** (SE 1.01, p=0.0008) |
| n high / low | 2,644 / 2,409 | 722 / 435 |

For context, the binary `why_now` on the same rows: +4.57pp (2025) and +2.88pp,
**p=0.047** (2026). The graded contrast reaches p=0.0006 on the same 2026 data. `docs/17`
§D flagged the binary's 2026 margin as fragile — two of five robustness specs pushed it
above .05. The graded version does not have that fragility. Same emails, same population,
sharper instrument.

**One null, reported:** "any occasion (≥1) vs none (0)" is +3.75pp, **p=0.23** in 2025.
Only 100 of 5,153 emails score 0, so there is no power there. This is why grade 0 was
excluded from the primary contrast in advance — and the exclusion is vindicated rather
than convenient.

---

## 3. Discriminant validity — it is not `research_signal` renamed

The disagreement crosstab raised a real threat. The graded pass calls 577 emails grade 4
that the binary pass called `why_now = false`, and the evidence it quotes for them is
recipient-specific *observation* rather than a dated event: "gearing up your Robotics
team", "impressed by how you're leveraging AI for contract intelligence". That is
`research_signal` territory — and **`research_signal` was a NULL in this study**. If the
graded scale had collapsed into it, the effect above would not be a why-now effect at all.

It has not:

| 2025, grade 4–5 → replied | estimate |
|---|---|
| alone | +4.43pp (p<0.0001) |
| controlling `research_signal` top-2-box | **+5.37pp** (p<0.0001) — control itself −1.71pp, p=0.22 |
| controlling `bespokeness` top-2-box | +4.51pp (p<0.0001) — control itself −0.17pp, p=0.90 |
| controlling the binary `why_now` | +3.45pp (p=0.0001) — **binary keeps +3.34pp, p<0.0001** |

Correlations: grade vs `research_signal` +0.56, vs `bespokeness` +0.48, vs binary
`why_now` +0.38 (2025). Related, not redundant.

Two readings follow, and both matter:

1. **Controlling for `research_signal` makes the grade effect *stronger*, and
   `research_signal` itself goes negative and non-significant.** The grade is doing the
   work. Whatever the two share, the predictive part belongs to the grade.
2. **Grade and binary survive together, each around +3.4pp.** They carry independent
   information. The graded scale is not a finer-grained binary; it adds something the
   binary could not see.

The 2026 column agrees throughout (+5.32pp controlling `research_signal`, p=0.024).

---

## 4. Why the two passes disagree — an instrument finding worth keeping

Agreement between grade ≥1 and binary `why_now` is only 71.2%, **kappa 0.142**. Both
directions of disagreement are informative, and they cut opposite ways.

| | count | reading |
|---|---|---|
| grade 1, binary **true** | 189 | The binary counted sender-side news as a why-now. "We recently released EMM-1", "We've recently onboarded Hudl." The graded pass demotes these to 1 — **exactly the Goodhart case this exercise was built to expose.** |
| grade 4, binary **false** | 577 | The binary read "occasion" strictly as a *dated event* and said no to recipient-specific observation. The graded anchors admit it at 4. |

So the binary was absorbing two different errors at once, in opposite directions. The
graded scale separates them, which is most of why it is both more repeatable and more
predictive.

**Consequence for how the confirmed finding is described.** "State a reason for writing
now" is too loose — 96.4% of cold pitches already clear that bar on the graded scale, and
the ones clearing it with sender-side news reply at 3.9%. The defensible instruction is
narrower: **the reason has to be about the recipient, and it should drive the ask.**

---

## 5. `docs/18` §C1's dead end is resolved — templating shallows the occasion

§C1 tested whether templates simply cannot carry a why-now and found they can: 70.7% vs
71.8%, identical. That closed the presence question. It could not ask about depth.

| 2025 | templated (n=2,767) | hand-written (n=2,386) |
|---|---|---|
| states an occasion (≥1) | **99.1%** | 96.8% |
| mean grade | 2.86 | 3.31 |
| **share at 4–5** | **42.1%** | **62.0%** |
| share 4–5 among those with any occasion | 42.5% | 64.0% |

Within-sender: templating costs **−0.52 grades** (SE 0.140, **p=0.0002**); −0.565 among
emails with any occasion (p=0.0001). 2026 points the same way but does not reach
significance on 327 templated rows (−0.28, p=0.22; −0.40 among ≥1, p=0.077).

**Templates state an occasion slightly more often and a specific one far less often.** The
first measured mechanism for the templating penalty. It is not that templates skip the
why-now — it is that a reusable body can only carry a reusable reason.

### How much of the penalty does this explain? 13%.

| 2025 | estimate |
|---|---|
| templated → replied, alone | −5.40pp (p<0.0001) |
| + grade 4–5 as a control | −4.69pp (p<0.0001) |
| **mediated by occasion depth** | **13%** |

2026: −3.79 → −3.42pp, **10%** mediated.

Stated plainly: **this is a real mechanism and a small one.** §C3 found all 19 counted text
features together explain 27% of the penalty; occasion depth alone accounts for about half
of that. The remaining ~87% is still unexplained by anything measured, and §C's
best-supported reading — recipients recognise mass mail and deprioritise it, evidenced by
the 4.8-day vs 1.8-day reply latency — is unchallenged by this result.

Do not let the mediation carry more weight than it can. 13% is a finding, not an
explanation.

---

## 6. What changes for a coaching tool

The binary could only say "include a reason." That is nearly useless as coaching — 96% of
mail already does, and doing it with sender-side news is worth 3.9%.

The graded scale supports the thing a coach actually needs: a ladder with a measured
payoff at each rung, and the largest single step at the top.

| instead of | write | 2025 reply rate |
|---|---|---|
| "we just raised our Series B" | — | 3.9% |
| "we're hosting a dinner in London" | — | 4.5% |
| "teams in your space are doing X" | — | 4.9% |
| "I saw your MirrorEye 5th-gen announcement" | ← recipient-specific | 7.4% |
| "…and wondered if consolidating CV pipelines is now front of mind" | ← **and it drives the ask** | **13.5%** |

The 4 → 5 step is the biggest in the table and the cheapest to teach: it is one clause
joining the observation to the request.

**Goodhart warning, unchanged and now quantifiable.** If a tool rewards "mentions an
occasion", it will be satisfied by grade 1 and buy nothing. If it rewards grade 4–5 it can
be gamed by fabricated specificity, which this study cannot detect at all — the judge sees
only the email, never whether the claimed fact is true.

---

## 7. Defects found and logged during this run

1. **The blinding gate gives different verdicts on identical bytes** (pre-registration
   §9.10). The same texts were CLEAN inside the 12,462-item corpus and BLOCKED on their own
   7,055-item subset, because the pruning rule takes its "is this an ordinary word"
   evidence from the corpus under test. All 14 flagged hits were read: every one a third
   party in body text — people met at events, a named peer, **the recipient's own
   colleague**, the Max Planck Institute — and none an Encord sender. Nothing was hidden:
   `max` and `kit` appear by name in the original run's reviewable pruned-as-ordinary list,
   which is the §9.7 structural fix working as designed. Gate deliberately left unchanged
   mid-spend; the guarantee for this run is byte-identity, pinned by
   `tests/test_whynow_batches.py`.
2. **The §5.3 silent-drop defect, third occurrence.** 9 of 161 batches returned 39, 38 and
   35 items for 40 inputs while every agent reported success. The assembly invariant caught
   it; the 14 items were re-run through a byte-identical prompt. The dropped items were
   ordinary 62–169-word cold pitches, not degenerate cases, so this is agent sloppiness
   rather than anything systematic — but **an agent's self-reported count remains worthless**.
3. **A merge collision silently disabled the secondary contrast.** The frame already
   carried `is_template_3plus`; re-merging it produced `_x`/`_y` and the script reported
   "not available" instead of failing. Fixed, and now an assertion.

---

## 8. What this does and does not license

**Does:** describing the confirmed why-now finding in the sharper form — recipient-specific,
and joined to the ask — with a measured gradient behind each rung. The instrument is the
most reliable in the study and survives every discriminant check run against it.

**Does not:** promotion to a confirmed finding. 2026 was already spent when this ran, so
the graded result has no clean out-of-sample test behind it, and the primary contrast was
declared after the binary result was known. It needs Aug 2026+ data, or an experiment.

Open items from `docs/18` §F, updated: **grade why-now 1–5 — DONE.** See §9 for what the
graded scale then made testable. Still open:
re-validate on Aug 2026+, A/B test the confirmed findings, get Amplemarket reply
attribution.

---

## 9. What the graded scale made testable — the templating mechanism, second pass

Added 2026-08-17 after §1–8, driven by operator questions during the readout. Reproducible:
`scripts/templating_mechanism_v2.py` → `output/templating_mechanism_v2.txt`.
EXPLORATORY, post-holdout, on used data.

`docs/18` §C2 asked "does the why-now work less well inside a template?", got p=0.216, and
the claim was withdrawn. **That test could not have worked.** A yes/no cannot tell a
specific reason from a generic one, so both sides of the interaction were the same mixture.
The graded scale separates them.

### 9.1 A specific reason does not pay inside a template

2025, cold pitches, **inbound-triggered openers removed** (see §9.2 — they are follow-ups to
a hand raise, not cold outreach):

| | generic reason (grade 1–3) | specific reason (grade 4–5) |
|---|---|---|
| **hand-written** | 5.2% (n=906) | **11.6%** (n=1,391) |
| **templated** | 3.7% (n=1,578) | 4.7% (n=988) |

A specific reason is worth **+6.4pp** hand-written and **+1.0pp** templated.
**Interaction −6.29pp, p=0.0001** (n=4,863).

Within-sender, on the full 2025 set: grade 4–5 → replied is **+6.31pp (p<0.0001)** among
hand-written mail and **+0.65pp (p=0.49)** inside templates. Read from the other direction,
the templating penalty is only −1.4pp among emails whose reason was generic anyway and
−5.6pp among those with a specific one — **most of what a good reason would have earned is
what templating takes away.**

2026 points the same way (+4.9pp hand vs +0.9pp templated) but the interaction is p=0.19 on
125 specific-reason templates. Underpowered, not contradictory.

**This reframes §5.** Templating shallowing the occasion (42% vs 62%) is real but mediates
only 13%. The larger fact is that climbing the ladder inside a template does not pay at all.
Those are different problems, and the second one is not fixable by writing better templates.

**Raw ratios, for the "2–4×" claim used in readouts:** 2025 templated 4.8% vs hand 9.3%
(**1.9×**); 2026 1.8% vs 8.0% (**4.4×**). Corner-to-corner in 2025, hand+specific vs
templated+generic, is 3.1×. So "2–4×" is defensible for the range across years; the single-
year templating effect is ~2× in 2025.

### 9.2 Template sub-types — a real split that is an inbound confound

Operator hypothesis: templates are not one thing. Blasting many people at one company
differs from a merge sequence hitting one person per company, and the latter can carry a
company-specific hook. Tested by how concentrated each template group's recipients are
across company domains (2025, 298 distinct templates):

| template group | sends | templates | mean grade | specific | inbound | reply |
|---|---|---|---|---|---|---|
| many people, few firms | 1,998 | 225 | 2.9 | 45% | 0% | 3.7% |
| mixed | 534 | 56 | 2.1 | 12% | 0% | 5.4% |
| one person per firm (merge) | 235 | 17 | 4.1 | **83%** | **30%** | **13.2%** |
| *hand-written reference* | *2,386* | — | *3.3* | *62%* | *8%* | *9.3%* |

The split is large and the third row appears to beat hand-written mail. **It does not
survive reading the templates.** Its three biggest are *"Just saw that you visited our
website and requested more information"* (n=70, 20% reply) and two variants of *"I hope you
found the interactive demo useful"* (n=50 and n=42). These are **follow-ups to an inbound
hand raise.** They reply well because the recipient already asked, and they legitimately
grade 4–5 because "you visited our site" *is* a recipient-specific checkable occasion.

The sub-type hypothesis is therefore **not supported**: the only template class that beats
hand-written mail is not cold outreach. Among genuinely cold templates the grades are low
and a specific reason still buys nothing.

**Wider consequence — worth carrying into any future frame build.** Inbound-triggered
openers are sitting inside the `cold_pitch` population. 8% of hand-written and 30% of
merge-template cold pitches contain an explicit hand-raise marker. They are a distinct
population with a mechanically different reply process, and they inflate whatever arm they
land in. Every number in §9.1 is computed with them removed; the pre-registered findings in
`docs/13`–`docs/16` are not, which is a known and previously unquantified impurity rather
than an error — the frame rule was route-and-type based, not trigger based.

### 9.3 The seam hypothesis — REJECTED

Operator argument, and it corrected a sloppy statement of mine. Saying "it is not the
writing, it is the reuse" cannot be right as stated: **the reader only ever sees one email
and cannot see that it was reused.** So a reader-side mechanism must be *in the text*.
Candidate: a specific fact welded onto a generic frame reads as bolted-on — the parts are
fine, the joint gives it away. We scored the parts and never the joint.

Operationalised with `bespokeness` ("could this have been sent to someone else unchanged"),
the closest measured proxy. If the seam were the mechanism, a specific reason inside a
bespoke body should beat one inside a generic body.

| 2025, grade 4–5 only | bespoke body | generic body |
|---|---|---|
| hand-written | 11.8% (n=871) | 11.8% (n=608) |
| templated | 3.9% (n=565) | 8.5% (n=600) |

The hand-written row is **flat to the decimal** — the surrounding body does not matter at
all when a human wrote it. The templated row runs backwards, and that is §9.2's confound
again: 29.5% of the generic-body cell is inbound-triggered vs 0% of the bespoke cell. With
those removed it is 3.9% vs 5.7%, still no seam effect.

And bespokeness does not absorb the interaction:

| model | interaction |
|---|---|
| raw | −5.39pp, p=0.0008 |
| + bespokeness | −5.38pp, p=0.0007 |
| + bespokeness × reason | −5.64pp, p=0.0002 |

**Rejected as measured.** This does not refute the operator's reasoning, which stands: if
the mechanism is reader-side it has to be in the text. It refutes `bespokeness` as the
carrier of it. The cue is not occasion depth (13%), not the 19 counted features (27%), not
judged bespokeness (0%), and not the seam as this proxy captures it.

**Where it plausibly still lives** — none of it measured by this study: sentence-level
phrasing and rhythm, word order, paragraph order, and genre familiarity (the reader has
seen this shape of email from other vendors). The operator flagged token-level analysis
earlier and correctly noted the corpus is too small for it. The non-text alternative is
unchanged: within-rep targeting, which no observational cut can separate.

### 9.4 Standing summary of the templating penalty

| explanation | share explained | status |
|---|---|---|
| all 19 counted text features together | 27% | `docs/18` §C3 |
| occasion depth (of that 27%) | 13% | §5 |
| judged bespokeness / the seam | ~0% | §9.3, rejected |
| copies sent (2 vs 25+) | 0% — a cliff, not a slope | `docs/18` §C4 |
| spam filtering | weak evidence against | `docs/18` §C5 |
| a few great templates carrying the rest | no — not a lottery | `docs/18` §C7 |
| **recipients recognise mass mail and deprioritise it** | **unquantified; best supported** | `docs/18` §C6 — replies arrive 4.8d vs 1.8d |
| within-rep targeting | unquantifiable observationally | needs an experiment |

The single most useful new fact is §9.1's: **the penalty is not something better wording
inside a template can recover.** One A/B test settles the rest — the same reason, in the
same email, sent as a template to half the list and typed for the other half.
