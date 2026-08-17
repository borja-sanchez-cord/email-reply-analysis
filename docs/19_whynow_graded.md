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

Open items from `docs/18` §F, updated: **grade why-now 1–5 — DONE.** Still open:
re-validate on Aug 2026+, A/B test the confirmed findings, get Amplemarket reply
attribution.
