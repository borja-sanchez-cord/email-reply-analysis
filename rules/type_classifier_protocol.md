# Opener type classifier protocol — pre-registered before any opener was classified

Openers are sorted into four types, analysed separately and never pooled (an event invite
getting replies must never masquerade as "well-written cold email").

| type | meaning |
|---|---|
| `cold_pitch` | first-touch selling: introduces the product/company to a prospect |
| `event_invite` | invitation to a webinar, dinner, conference booth, meetup, roundtable |
| `post_event_followup` | "great to meet you at X", follow-up naming a specific past event/meeting |
| `other` | recaps, scheduling logistics, content shares, replies mislabelled as openers, anything not confidently one of the above |

Rules:

- Classified from **subject + cleaned body only** (quoted trails stripped). No outcome, no
  sender identity, no date shown.
- Agent batches of ~80, structured output; `other` is the required answer when unsure —
  forcing a type is worse than admitting ambiguity.
- **Audit before trust**: 20 random examples of each assigned type are printed and read;
  systematic errors → fix classifier → re-run → re-audit. The audit happens before any
  reply-rate-by-type number is computed.
- Openers classified `other` that are actually recaps/scheduling are thereby excluded from
  cold-pitch analysis automatically (they fail the "cold pitch" type test).
- Post-event follow-ups: if the group is large enough, timing (days since the named event,
  where inferable) is tested; otherwise this is reported as too small and dropped.
- The classifier also flags `is_reply_like` (text reads as a mid-conversation message) as a
  safety net on top of the thread-based exclusion.
