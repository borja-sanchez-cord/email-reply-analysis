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

## Mechanics

- Batches of ~40 (12 dimensions × 40 emails is a full agent's honest workload).
- A random **10% is re-scored** by a second agent run; per-dimension agreement
  (exact + within-1) is reported. Dimensions with poor repeatability are flagged and any
  conclusion built on them downgraded in the report.
- Judges are told to rate what is on the page, not to infer quality from length or genre.
- Event invites and cold pitches are judged with the same rubric (analysis never pools
  them; `ask_size`=large is expected for invites).
