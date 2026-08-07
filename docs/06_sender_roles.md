# Sender role resolution — the corpus-defining decision

Committed BEFORE any reply-rate-by-sender or reply-rate-by-feature number existed.

## Problem

188 of 236 HubSpot owners have no team; team membership is today's snapshot; high-volume
senders include marketing, growth, CS/AM and leadership. Excluding all unknowns would
discard three quarters of the clean mailbox corpus.

## Method (three independent evidence streams, no outcome data used)

1. **Team membership** (owners API, active+archived): the eight `<vertical> <region> CA(s)`
   teams → 31 team-CA locals. Known weakness: snapshot-only.
2. **Send-time signatures**: role lines extracted from each sender's own emails
   ("Commercial Associate", "Growth", "Customer Success Manager", "Head of Sales" …).
   Discovery: **CA = Commercial Associate**; CAs use cover titles ("AI // ML // Computer
   Vision", "GTM", "ML Partnerships").
3. **Blind style characterisation**: 67 agents (one per sender with ≥20 clean mailbox
   openers) each read 8 random openers by that sender and judged the work:
   one-to-one researched selling vs mass event/webinar blasts vs existing-customer
   account mail vs leadership correspondence. No agent saw any outcome, date, or
   hypothesis. Output: `output/sender_role_verdicts.json`, 67/67 completed.

## Result (`output/sender_roles.csv`)

| class | senders | G30 clean mailbox openers |
|---|---|---|
| **confirmed_ca** (team + behaviour agree) | 21 | 7,406 |
| **fallback_ca** (behaviour CA-like; owner archived/teamless) | 17 | 8,238 |
| **not_ca** (marketing/growth 14, post-sales 11, leadership 4) | 29 | 22,460 |
| unclassified (<20 openers each) | ~30 | 50 |

Notable corrections in both directions:
- **Team-CAs excluded by behaviour** (7): leo (Head of Sales), nick (Head of Physical AI),
  arisha (Customer Success Manager), shivant (Strategic Account Manager), alyssa (Account
  Manager), tom.inglis (Account Executive), william. Team lists alone would have polluted
  the corpus with CS/AM/leadership mail.
- **Archived owners recovered as CAs** (17, incl. winnie, skander, shreya, charlotte, kat*,
  jamie, sara): departed reps whose send-time behaviour is unmistakably CA outbound.
  (*kat is also team-CA; listed under confirmed.)
- **Marketing/Growth identified** (14, incl. thao with 10,304 openers — the single biggest
  sender): webinar/newsletter/event blasts. Their volume would otherwise dominate any
  "cold email" analysis.

## Rules for analysis

- **Q1 corpus** = clean mailbox openers from `confirmed_ca` + `fallback_ca` senders,
  filtered to type `cold_pitch` (and separately `event_invite` etc.) by the blind type
  classifier. Results reported for the two CA classes both pooled and separately.
- Medium-confidence verdicts (colin, sara, dillon, james.watson, nick.aguilar → CA;
  william, kevin, nicolaj.peters → not-CA) are flagged; headline findings re-checked with
  them excluded.
- Senders with <20 openers (50 openers total) are excluded and counted.
- Limitation stated in the report: role labels are inferred from behaviour and signatures;
  a rep who changed roles mid-window carries one label.
