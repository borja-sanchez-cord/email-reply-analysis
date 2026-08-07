# Field choices for the pull — chosen from evidence, not copied

Date: 2026-08-07. Method: pulled the full property catalogue for the email object
(129 properties → `data/email_properties.json`), then probed fill rates on ~600 emails in
each of three months spread across the window (2025-03, 2025-11, 2026-05), split by
direction (`scripts/probe_fill_rates.py`). The sample is the first 600 emails of each month
by timestamp, not a random sample — good enough for "is this field ever filled", which is
all it is used for.

## What the probe established

| Fact | Evidence |
|---|---|
| `hs_object_source` cleanly separates mailbox sends from sequencer sends | Values seen: `EMAIL` (mailbox sync), `INTEGRATION` (sequencer), `CRM_UI` (rare). `hs_object_source_detail_1` names the integration: "Apollo Integration", "Amplemarket". 100% filled in all three months. |
| Mailbox-only fields exist and track the mailbox share | `hs_email_thread_id`, `hs_email_message_id`, `hs_email_logged_from`, `hs_incoming_email_is_out_of_office` are filled on essentially all mailbox emails and no sequencer emails (71% → 35% → 5% on outgoing, tracking the sequencer ramp; 100% on incoming). |
| `hs_in_reply_to_engagement_id` is unusable | 0% filled in all three months, both directions. |
| `hs_email_sent_via` is sparse and only ever GMAIL | 30%/25%/1% on outgoing. Kept only as a descriptive field; per the brief (trap 2) it is never used to mean "automated vs hand-written". |
| `hubspot_owner_id` is incomplete on outgoing emails | 84% / 55% / 71% filled. Sender attribution must fall back to `hs_email_from_email`. |
| Volumes confirm the documented ramp | Portal totals in the probe windows: 2025-03 ≈ 6.7k, 2025-11 ≈ 17.1k, 2026-05 ≈ 26.9k emails/month. |
| `hs_email_headers` is always filled but heavy | Excluded from the bulk pull; can be fetched selectively if ever needed. |
| `hs_incoming_email_is_out_of_office` is 100% filled on incoming | Kept as an auxiliary signal only; the reply classifier works from text (per the brief) and this flag is checked against it, not trusted blindly. In the probe it was true on 2/145 incoming. |

## Metadata pulled for EVERY email (the universe pull)

| Property | Why |
|---|---|
| `hs_timestamp`, `hs_createdate` | When it happened; dedup/QC |
| `hs_email_direction` | outgoing vs incoming vs forwarded |
| `hs_email_status` | SENT vs BOUNCED (partial fill, outgoing only) |
| `hs_email_subject` | classification, features |
| `hs_body_preview` | first ~few hundred chars; QC and cheap triage |
| `hs_email_from_email`, `hs_email_to_email`, `hs_email_to_raw`, `hs_email_cc_email` | who → whom; the `to` field needs display-name parsing |
| `hs_email_thread_id`, `hs_email_message_id` | threading for reply attachment |
| `hs_object_source`, `hs_object_source_detail_1`, `hs_object_source_label` | mailbox vs sequencer (the load-bearing split) |
| `hs_email_sent_via`, `hs_email_logged_from` | descriptive only |
| `hubspot_owner_id`, `hubspot_team_id` | rep attribution (with from-email fallback) |
| `hs_incoming_email_is_out_of_office` | auxiliary OOO signal on incoming |
| `hs_email_bounce_error_detail_message` | bounce detection |

Bodies (`hs_email_text`, `hs_email_html`) are pulled in a separate batch-read pass for the
subsets that need them: all incoming emails (reply classification) and all candidate openers
(type classification + features). Pulling ~380k full bodies up front would be several GB for
no analytical gain; every email whose text any step reads is fetched in full.

## Deliberately NOT used for findings

- `hs_in_reply_to_engagement_id` — empty.
- `hs_email_reply_count`/open/click counts — sparse (≤22%), tracker-based, direction-biased.
- `hs_email_sent_via` — per the brief, says how it was sent, not who wrote it.
- Account-tier fields on companies — hold today's values, not send-time values (brief, trap 4).
- Contact persona fields — brief says empty; verified on our own pull before discarding.
- `hs_email_open_rate` etc. — downstream of tracking configuration, not of writing.

Contacts, companies and owners: pulled with fields chosen after inspecting their own
property catalogues (`data/contacts_properties.json`, `data/companies_properties.json`);
fill rates computed on our own pull and reported in the write-up, not assumed.
