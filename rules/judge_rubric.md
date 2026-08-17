# AI-judge rubric — committed before any email was scored

Derived from reading first-touch CA emails before any outcome data existed: ~112 read
directly during corpus checks, plus 400 read by four blind rubric-mining agents
(`output/rubric_dimension_proposals.json`) whose proposals converged. Every dimension
below showed real variation in those 500+ emails, with quoted evidence in the proposals
file. Dimensions requiring information outside the email text were rejected.

## Blinding (rule 1, the most important in the study)

The judge sees the subject + body only, after redaction: recipient first name → `[NAME]`,
recipient company → `[COMPANY]`, URLs → `[LINK]`, signature/footer block removed. The
judge never sees: whether the email got a reply, the sender, the date, or any hypothesis.

## Scored dimensions (each with anchors shown to the judge)

| # | dimension | scale | what 5 looks like / what 1 looks like |
|---|---|---|---|
| 1 | `research_signal` | 1–5 | 5: cites a concrete, checkable fact about this recipient/company (their product, benchmark result, talk, funding, named referrer). 1: nothing beyond the name slot. |
| 2 | `why_now` | yes/no | An explicit, checkable occasion for reaching out now (launch, event, visit, referral). |
| 3 | `value_specificity` | 1–5 | 5: quantified/mechanistic ("reduce data ops overhead 60%", named capability tied to outcome). 1: "bring better models to market, faster". |
| 4 | `proof_relevance` | 0–5 | 0: no customer/social proof. 5: named customers that are recognisably the recipient's direct peers. 2: marquee logos irrelevant to their world. |
| 5 | `pain_hypothesis` | 1–5 | 5: articulates a specific plausible pain in their workflow ("keeping recognition models sharp across spoofing attempts…"). 1: no hypothesis about the reader. |
| 6 | `ask_clarity` | 1–5 | 5: exactly one CTA with format/duration/concrete times. 1: no ask or several competing asks. |
| 7 | `ask_size` | categorical | `no_ask` / `tiny` (reply or thumbs-up) / `small` (coffee, booth drop-by, 15–20 min) / `medium` (30 min call, demo) / `large` (attend an event, big commitment) |
| 8 | `bespokeness` | 1–5 | 5: could only have been written for this person. 1: visible mail-merge shell (broken fields, "Hi ,", swapped-company-only). |
| 9 | `polish` | 1–5 | 5: flawless. 1: typos, garbled merge artefacts, collapsed formatting, duplicated blocks. |
| 10 | `economy` | 1–5 | 5: every sentence earns its place. 1: long blurbs, repeated context, rambling. |
| 11 | `peer_tone` | 1–5 | 5: collegial, curiosity-framed, low pressure. 1: sales script, urgency/scarcity mechanics. |
| 12 | `recipient_centricity` | 1–5 | 5: mostly about their world. 1: mostly about us (our founders, our funding, our features). |

Analysis split (pre-registered in `rules/analysis_splits_addendum.md`): 1–5 scales use
top-2-box (4–5) vs rest; `why_now` as is; `ask_size` compared across its levels; a
`proof_relevance` secondary contrast is 0 (no proof) vs ≥1 (any proof).

## Middle anchors (2/3/4) — appended before any email was scored

The table above defined only the endpoints. The §1b intent gate failed at 83.3% for exactly
one reason: an undefined boundary that two competent readers split differently
(`docs/11_intent_accuracy_gate.md`). These middle anchors close the same hole before any
judging spend. Committed before Layer-1 results existed and before a single email was
judged; written from the same 500+ outcome-blind emails as the endpoints.

The analysis split is top-2-box (4–5 vs 1–3), so the **3/4 boundary is the one that decides
every result** — each pair below is written to make that line sharp.

**Tie-break rule:** score what is on the page. If an email sits between two anchors, take
the LOWER score. A judge must never award a point for something it inferred, assumed, or
found plausible but unstated.

| # | dimension | 2 | 3 | 4 |
|---|---|---|---|---|
| 1 | `research_signal` | Segment-generic: a claim that fits any company in their space ("teams building CV models like yours"). | One true recipient-specific fact, but obvious from the company homepage or the name of their field — no research needed to write it. | A concrete, checkable fact about them (product line, named model, benchmark, talk, funding round) — but mentioned in passing, not connected to the pitch. 5 requires the fact to do work. |
| 3 | `value_specificity` | Generic benefit with a category word attached ("improve your annotation workflows"). | Names a concrete capability tied to what they do, but no mechanism and no number ("curate the edge cases your team is missing"). | Has a mechanism OR a number, but not both, or the claim is quantified yet not tied to the recipient's own outcome. |
| 4 | `proof_relevance` | Named marquee logos with no relation to their world (as defined at left). | Named customers from an adjacent field — plausibly relevant, recognisably not their peers. | Named customers in the recipient's own field, but a reader would need a moment to see the match. 5 is instant: their direct peers, no thinking required. |
| 5 | `pain_hypothesis` | An industry-wide commonplace ("labeling is expensive and slow"). | Pain matched to their segment or use case, but phrased so it fits every company in that segment. | A specific pain that is plausibly *theirs*, asserted without any evidence from their world. 5 grounds it in something checkable about them. |
| 6 | `ask_clarity` | An ask exists but is buried or hedged to mush ("would love to connect at some point"). | Exactly one clear ask, missing every concrete detail — no duration, format, or times. | One clear ask with duration or format stated, but no proposed times; or a dominant ask with a second minor one trailing it. |
| 8 | `bespokeness` | Clean mail-merge: name and company slots filled correctly, nothing else would change for a different recipient. | A template plus ONE personalised sentence or clause. | Several elements written for this person, on a still-recognisable skeleton. 5 has no visible skeleton at all. |
| 9 | `polish` | Multiple errors, or one glaring merge artefact ("Hi ,", `{{first_name}}`). | A few minor typos or awkward phrasings; no broken fields. | Clean; at most one trivial slip a reader might not notice. |
| 10 | `economy` | Noticeably padded — repeated context, a long company blurb — but a discernible point. | Mostly on-point; one paragraph or block could be cut without loss. | Tight; a single redundant clause or sentence at most. |
| 11 | `peer_tone` | Salesy register — presumptive closes, flattery, exclamation pressure — without explicit urgency/scarcity mechanics. | Neutral and professional but transactional; neither pressure nor genuine curiosity. | Collegial and low-pressure with one slip into pitch language. |
| 12 | `recipient_centricity` | Mostly about us, with a token nod to them (one clause). | Roughly balanced halves — as much about us as about them. | Mostly about their world, with a short necessary us-section. |

No middle anchors exist for `why_now` (#2, yes/no) and `ask_size` (#7, categorical) —
they have no scale to anchor. For `proof_relevance`, 0 = no proof of any kind and
1 = unnamed proof ("hundreds of AI teams trust us"); the 2–4 anchors above complete
that scale.

## Mechanics

- Batches of ~40 (12 dimensions × 40 emails is a full agent's honest workload).
- A random **10% is re-scored** by a second agent run; per-dimension agreement
  (exact + within-1) is reported. Dimensions with poor repeatability are flagged and any
  conclusion built on them downgraded in the report.
- Judges are told to rate what is on the page, not to infer quality from length or genre.
- Event invites and cold pitches are judged with the same rubric (analysis never pools
  them; `ask_size`=large is expected for invites).

---

# Addendum: `why_now_grade` (0–5) — a graded replacement for the yes/no

Written 2026-08-17, **before a single email was graded**, on the operator's instruction
(`docs/18` §F open item). Committed first for the same reason the middle anchors were:
anchors written after seeing results are not anchors.

## Why grade it at all

`why_now` (yes/no) is the study's strongest confirmed positive lever — +4.6pp in 2025,
+2.9pp on the sealed 2026 hold-out — and its most repeatable judgment (kappa 0.716,
two independent Sonnet runs agreeing 90.9%).

But 80.3% of judged emails already score `true`, and 70.7% of *templated* emails do
(`docs/18` §C1). So "state a reason for writing now" is already nominally complied with,
which is precisely where Goodhart bites: a coaching tool built on the binary would tell
reps to do a thing most of them already do. The question the binary cannot answer is
whether a **specific** occasion beats a **generic** one. That is what this scale measures.

## The scale

One question, asked of the same blinded text: **how specific and checkable is the stated
occasion for writing now?**

The 3/4 boundary decides every result under the split declared below, so it is written to
be sharp. It is a single test: **is the occasion about THIS recipient, or about their
category / about us?**

| grade | anchor |
|---|---|
| **0** | **No occasion.** Nothing explains why this week rather than any other. "Just wanted to reach out", "I've been meaning to connect." |
| **1** | **Sender-side manufactured.** An occasion that exists only on our side and would read identically to any recipient on any day: our funding round, our new feature, our expansion into their region, the quarter ending. |
| **2** | **A real event, offered to a list.** Genuinely time-bound and checkable, but not tied to this recipient — a dinner, a conference booth, a webinar. The same sentence works for everyone invited. |
| **3** | **Tied to their category.** Their industry had news, a competitor shipped something, a regulation lands, "teams like yours are doing X this quarter." True and timely for their segment; not for them. |
| **4** | **Tied to THIS recipient, checkable.** They launched a product, raised a round, published a paper, spoke somewhere, visited our site, or a named person referred us — stated, but left sitting next to the ask rather than driving it. |
| **5** | **The same, and it does the work.** The recipient-specific occasion *is* the reason for the ask; the two are logically joined, so this email could not have been sent last month. |

**Tie-break, inherited unchanged:** score what is on the page. Between two anchors, take
the LOWER grade. Never award a point for an occasion inferred, assumed, or plausible but
unstated.

## Pre-declared analysis split

**Primary contrast: top-2-box (4–5) vs (1–3), restricted to grade ≥ 1.**

Grade 0 is excluded from the primary contrast on purpose. "Occasion vs no occasion" is
already answered by the confirmed binary finding; re-running it here would be the same
test with a new name. The new question is conditional — *given* that an email states an
occasion, does a recipient-specific one beat a generic one? — so the population is emails
that state one.

- Population: cold pitches in frame G30 (the population the binary finding was estimated
  on). Event invites are excluded: an invitation's occasion *is* the event, so the scale
  has no room to vary.
- Spec: the study's §3 primary spec, unchanged — LPM, sender fixed effects, SEs clustered
  on sender. Both outcomes (`replied`, `interested`), as every finding carries both.
- Length control via `scripts/length_control.py`, because occasion-specificity plausibly
  proxies for a longer email.

## Pre-declared reliability gate — the number that decides whether any of this is used

A 10% random subset (seed **20260817**) is graded a second time by an independent agent
run, identical prompt, separate output directory.

**Gate: Cohen's kappa on the 4–5 vs 1–3 split — the split the analysis uses — computed
among items both runs graded ≥ 1.**

| kappa | consequence |
|---|---|
| **≥ 0.50** | the scale is usable; the effect estimate is reported |
| **< 0.50** | the scale is **binned**. No effect estimate from it enters any deliverable, and the failure is written up. |

Raw agreement is not the gate. `economy` agrees 75.8% and has kappa 0.22, because 88% of
its mass sits in one box — the lesson is already in the record and is not being relearned.

**The gate is evaluated before any reply outcome is joined.** Operationally enforced: the
agreement script reads the two score sets only, and never opens the frame.

Three further numbers are reported with no gate attached, because they describe the
instrument rather than the result:

1. **kappa on 4–5 vs 0–3, unconditioned** — the conditioning above is a choice, so the
   unconditioned figure is shown next to it.
2. **kappa on 0 vs ≥1** — does the graded pass agree with itself about whether an occasion
   exists at all.
3. **grade 0 vs binary `why_now == false` agreement** — two passes, months apart, on the
   same question. Disagreement here is a fact about the instrument and is reported whether
   or not it is convenient.

## Status: exploratory, and it cannot become anything else

The 2026 hold-out was opened and scored on 2026-08-15 (`docs/16`). It is spent. A graded
result on 2026 is a **second look at used data** and carries the same status as everything
in `docs/18` — suggestive, not confirmatory. Nothing in this addendum can confirm,
strengthen, or weaken the pre-registered binary finding, which stands on its own
pre-registered test. Promoting the graded scale to a confirmed finding requires fresh
data (Aug 2026 onward) or an experiment.
