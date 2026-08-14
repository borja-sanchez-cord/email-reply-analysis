# Why Amplemarket is excluded — text for the report

**Must appear in `output/REPORT.md`.** Corrected 2026-08-14 (see "Two wrong versions" below —
the earlier explanations were wrong and are kept on the record rather than deleted).

## The reason, plainly

Apollo and Amplemarket both write their **sent** emails into HubSpot. Neither writes a
HubSpot thread id — that field only exists on mailbox-synced mail. The difference is the
**inbound** side:

| | outbound rows | carry a thread id | inbound rows |
|---|---|---|---|
| mailbox sync (Gmail) | 128,060 | 100% | 21,210 |
| Apollo | 85,059 | 0% | **75,177** |
| Amplemarket | 62,392 | 0% | **979** |

**Apollo logs the rep's whole inbox back into HubSpot.** So its replies are readable
directly, no thread needed.

**Amplemarket logs sends only.** Its replies reach HubSpot only when Gmail sync happens to
catch them — and they then carry a thread id pointing at a thread containing no Amplemarket
message, because the Amplemarket copy has no thread id. The reply is present but
unattachable.

This is a product decision by each vendor, not a HubSpot limitation.

## What that costs

| | our thread-based matching finds | inbound from that recipient actually exists |
|---|---|---|
| mailbox | 15.68% | 13.80% |
| Apollo | 11.47% | 11.84% |
| **Amplemarket** | **1.18%** | **3.35%** |

Apollo and mailbox: matching finds essentially everything. Amplemarket: it finds about
**one third**. Including Amplemarket at the study's matching standard would record ~65% of
its real replies as "no reply".

Amplemarket's own dashboard reports a 2.4% reply rate, against the 3.35% our
address-level probe finds — the two are consistent, which is the check that the 3.35% is real.

## Wording for the report

> Amplemarket sends are excluded. Amplemarket writes its sent emails to HubSpot but not the
> replies, and its records carry no thread id, so a reply that arrives via the mailbox has
> nothing to attach to. Thread-based matching — the standard used everywhere else in this
> study — recovers only about one in three Amplemarket replies. Those replies can be
> recovered by matching on the recipient's address instead, but that is a looser standard
> than the rest of the study uses, and applying two different matching standards inside one
> outcome variable would make the outcome incomparable across channels. Amplemarket sends
> still count as **touches** in the follow-up curve; they are simply not scored for content.

Plus the simpler reason: Amplemarket is automated bulk sending (30,390 leads over 12 months).
This study measures emails a rep sent from their own mailbox. Different activity, different
question.

## Two wrong versions, kept on the record

1. *"Amplemarket has no inbound log"* (run 1, `docs/03`). **Wrong.** 979 inbound rows exist,
   spanning 653 sender domains, including bounces and out-of-office. A log exists.
2. *"Amplemarket fails to sync about a third of its replies"* (this file's first version).
   **Wrong, and backwards.** The replies are in HubSpot. Our matching cannot link them.

Both were corrected only because the vendor's own docs were read
(https://knowledge.amplemarket.com/articles/8661663156-integrating-with-hubspot — "when the
lead replies to a stage, we also add the email message as an 'Engagement'") and the operator
supplied the Amplemarket analytics export. Neither correction came from the pipeline, which
is the point: the pipeline reproduced the same wrong answer every time.

## Contrast worth reporting, with its caveat

| | interested rate |
|---|---|
| Amplemarket (own dashboard, 30,390 leads) | 1.8% |
| Hand-sent cold pitches (this study) | 4.5% |

Different tools, different targeting, different matching — **not** a controlled comparison and
must not be stated as one. Useful only as a directional sanity check from a system independent
of this pipeline.

## Still open (does not block)

Whether the two-thirds we cannot link differ systematically from the third we can. Not
resolvable inside HubSpot. Named as a limitation.
