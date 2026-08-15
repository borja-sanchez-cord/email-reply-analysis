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
