# Opener type classifier — audit before any reply-rate-by-type number is used

Tool: `scripts/audit_types.py` (prints the exact text the classifier saw).
Protocol: `rules/type_classifier_protocol.md`, committed before classification began.

## Read examples of each assigned type

**`cold_pitch`** — correct. Examples read were genuine first-touch selling: a LiDAR
product-launch pitch, a researched medical-imaging pitch naming the prospect's own
pipelines and their peers (Aignostics, Paige.ai), a conference coffee ask with a
company-specific hook, and a "researching how AI/ML teams are solving data annotation…
would you be open to a 15-minute call" outreach. Both bespoke and templated pitches are
present, which is correct — templating is a *measured feature*, not a type.

**`event_invite`** — correct. Webinar blasts ("Invite: How top AI teams are scoring
generative models", repeated verbatim), a CVPR booth + happy-hour invitation, and a
personally-framed AWS Loft evening invite. Mass and personalised invites both land here as
specified, because the primary ask is attendance.

**`post_event_followup`** — correct. "How was CVPR?" post-conference outreach and similar
messages referencing a specific past interaction.

**`other`** — correct and doing real work. Examples: a misdirected-thread reply ("did you
mean to send this to me?"), a post-call recap with a recording link and next steps, a
restaurant booking exchange, a customer-success introduction ("I wanted to introduce myself
as your new CSM"), and a logistics note about a mock call. Exactly the recap /
scheduling / account-management traffic the brief says to keep out of the cold-email
analysis.

## The `is_reply_like` safety net

The classifier separately flags text that reads as mid-conversation. Cross-tab of assigned
type against that flag (labels available at audit time):

| type | not reply-like | reply-like | % reply-like |
|---|---|---|---|
| cold_pitch | 6,688 | 307 | **4.4%** |
| event_invite | 8,964 | 86 | 1.0% |
| post_event_followup | 250 | 201 | 44.6% |
| other | 450 | 1,372 | **75.3%** |

Two things follow:

1. The flag agrees with the type assignment where it should — `other` is three-quarters
   mid-conversation traffic, `event_invite` almost none.
2. About **4% of "cold pitches" are actually mid-conversation messages** whose thread had
   no `thread_id` recorded, so the structural exclusion in `build_pushes.py` could not
   catch them. These are now excluded from the analysis corpus by the safety net
   (`build_frame.py`), and the count is reported in the eligibility waterfall.

This is precisely the failure the brief warns about — a bump scored as an opener — caught
by a second, independent check rather than assumed away.

## Not forced

Anything the classifier could not confidently place stays in `other` by instruction, and
`other` is never pooled into the cold-pitch results. Post-event follow-ups are a small
group; whether their timing sub-analysis is possible is decided on the final counts and
reported either way.
