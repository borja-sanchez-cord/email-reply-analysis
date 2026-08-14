# Why Amplemarket is excluded — text for the report

Operator-approved wording (2026-08-14). **Must appear in `output/REPORT.md`.**

1. Amplemarket says 2.4% of its emails get a reply.
2. HubSpot only has a record of about 1.6%.
3. So roughly 1 in 3 Amplemarket replies never arrives in HubSpot.
4. We can only see what's in HubSpot. So for those missing ones, we'd write down
   "nobody replied" — when someone did.
5. That's counting missing data as failure. It would make Amplemarket look worse than
   it is and drag the study's numbers down for no reason.

Plus the simpler reason: Amplemarket is automated bulk sending (30,390 leads). This study
measures emails a rep wrote and sent from their own mailbox. Different activity, different
question. Amplemarket sends still count as **touches** in the follow-up curve — they close
gaps — they just aren't scored for content.

## Evidence

**External, primary source.** Amplemarket's own docs say replies *are* synced:
"When a stage is sent to a lead or when the lead replies to a stage, we also add the email
message as an 'Engagement' to the 'Contact' on HubSpot."
(https://knowledge.amplemarket.com/articles/8661663156-integrating-with-hubspot)

So the earlier run-1 conclusion — "Amplemarket inbound does not exist" — **is wrong.**
A log exists. It is incomplete, not absent. Corrected here.

**Operator's Amplemarket dashboard** (Analytics → Overview, last 12 months):

| metric | value |
|---|---|
| new leads | 30,390 |
| email open rate | 47% |
| **email reply rate** | **2.4%** |
| leads interested | 683 (1.8%) |
| meetings booked | 243 (0.8%) |

**Our HubSpot pull:** 979 Amplemarket inbound rows against 62,392 Amplemarket outbound
rows = **1.57%**. Against the vendor-reported 2.4%, capture is ~65%; about a third of
replies are missing.

The 979 rows are a genuine log, not noise: they span 653 distinct sender domains and
include bounces, out-of-office and foreign-language auto-replies alongside real replies.
They start 2025-11, which is when Amplemarket use itself started.

## Contrast worth reporting

| | interested rate |
|---|---|
| Amplemarket (its own dashboard) | 1.8% |
| Hand-sent cold pitches (this study) | 4.5% |

~2.5x. Different tools and different targeting, so **not** a clean comparison and it must
not be stated as one — but it comes from the operator's own systems, independent of this
study's pipeline, and is a useful sanity check that the two numbers are the right way round.

## Still open (does not block)

Whether the missing third is random or systematic. If Amplemarket fails to sync the
*interested* replies specifically, the 1.8% is itself understated. Not resolvable from
HubSpot. Named as a limitation.
