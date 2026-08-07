# Reply classifier accuracy — the check that matters most

The reply label *is* the outcome variable. If it is wrong, every finding is distorted. The
pre-registered check (`rules/reply_classifier_protocol.md`) was run as specified.

## Method

300 reply candidates drawn at random. Two independent labelling passes:

- **Pass A (production)**: the taxonomy classifier — "assign one of 9 categories, then an
  intent". 209 agent batches, blind: reply text only, quoted trails stripped, no sight of
  the outgoing email, sender, date or outcome.
- **Pass B (accuracy check)**: a deliberately *different question* — "describe in 2–3
  sentences what this email is and what kind of process produced it (a person typing, an
  autoresponder, a mail server, a scheduling tool…), then say what the writer wants."
  Free-text description first; the label was derived mechanically afterwards
  (`scripts/reply_accuracy.py`) from the `producer` field. Different question → different
  mistakes, which is the point.

## Result

**Agreement on "Replied" (a real human wrote back): 99.0% — 295 of 298** (1 of the 300 was
`cannot_tell` in pass B and excluded; 1 had no pass-A label at the time of the run).

Pass A calls 67.1% of reply candidates human; pass B 66.1% — the passes agree on the base
rate as well as case-by-case.

Full cross-tab (`output/reply_accuracy/agreement.csv`):

| pass A ↓ / pass B → | person typing | calendar tool | ticketing | subscription | autoresponder | other machine |
|---|---|---|---|---|---|---|
| human (200) | **197** | 1 | 2 | 0 | 0 | 0 |
| calendar_bot (36) | 0 | **36** | 0 | 0 | 0 | 0 |
| other_bot (52) | 0 | 0 | 26 | 23 | 0 | 3 |
| out_of_office (8) | 0 | 0 | 0 | 0 | **8** | 0 |
| auto_ack / security_scan (2) | 0 | 0 | 0 | 0 | 1 | 1 |

## Direction of the disagreements — all three are the same case

Every disagreement is **a human sentence delivered inside a machine wrapper**:

1. Venue manager's comment ("All set - see you tonight!") sent through the Tripleseat
   event platform — pass A: human; pass B: ticketing system.
2. A second Tripleseat venue comment about billing — same pattern.
3. A calendar *decline* carrying a typed note ("I will be on holidays on 10th April") —
   pass A: human/not_now; pass B: calendar tool.

Pass A's treatment is the one **pre-registered before any data was seen**: "auto-generated
text with a human sentence appended → `human` (the human sentence wins)". So these are not
errors against the rule; they are pass B keying on the delivery mechanism instead of the
writer. There is **no case in the sample where pass A invented a human reply that pass B
saw as pure machine output**, and none where a real human reply was missed as a bot.

No fix was required, so no re-measurement was needed. Two notes carried into the report:

- The residual risk is concentrated in *logistics* humans (venue staff, calendar notes)
  rather than prospects; where such a message is the only reply to a push, that push counts
  as Replied. This is rare in the CA cold-pitch corpus by construction (the recipient must
  be the prospect the opener was sent to).
- `calendar_bot` is 12% of reply candidates — machine "Accepted:" notices. Counting those
  as replies would have inflated reply rates substantially; they are excluded.

## Interested-level check

Among replies both passes call human, pass A marks 48% as Interested. Spot-checking pass
B's independent free-text "what the writer wants" against pass A's intent shows the two
line up: A-`wants_call` ↔ "to confirm a meeting time"; A-`asks_question` ↔ "ask what its
purpose would be… confirm whether their volumes fit"; A-`not_interested` ↔ "to decline
the sales pitch and close the conversation politely".

One systematic gap is visible and reported: several replies pass A labelled `other_human`
are described by pass B as forward motion ("to deliver the signed NDA and move the trial
process forward", "to communicate the expected data volume for the evaluation"). These are
*existing-deal* logistics rather than new interest, so the conservative labelling is the
right call for a cold-outreach study — but it means **Interested is a slight
under-count**, not an over-count. Stated in the report.
