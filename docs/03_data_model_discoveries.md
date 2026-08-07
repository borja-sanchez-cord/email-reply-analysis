# Data-model discoveries that reshape the pipeline (found before any results)

Date: 2026-08-07, immediately after the universe pull (379,945 emails after dedup;
358,596 direction=EMAIL, 21,340 INCOMING_EMAIL, 9 FORWARDED).

## 1. Four internal sending domains, not one

Outgoing sender domains: encord.com (127.9k), **encord.ai (129.6k)**, **tryencord.com
(23.9k)**, cord.tech (1.0k). The alt domains are used both by sequencers AND by real
mailbox sync (source=EMAIL: encord.ai 42.5k, tryencord.com 22.5k rows) — reps run real
alt-domain mailboxes for outbound. Sender identity therefore resolves by **local part
across the four internal domains** (hugo@encord.ai = hugo@encord.com), with ambiguous
local parts (e.g. james@tryencord.com vs three james.* owners) resolved from evidence or
left unclassified — never guessed.

## 2. Apollo logs the rep's whole inbox into HubSpot as direction=EMAIL

Subject-prefix taxonomy of INTEGRATION-sourced rows:

| pattern | meaning | count |
|---|---|---|
| `[Apollo] [Email] [>>] …` / `Email: >> …` | Apollo-logged **outbound** | 65,676 + part of 21,646 |
| `[Apollo] [Email] [<<] …` / `Email: << …` | Apollo-logged **inbound** (prospect replies, calendar accepts, and also newsletters/notifications — the whole inbox) | 72,914 + part of 21,646 |
| Amplemarket rows (no marker) | outbound sends (62.4k internal-sender of 63.4k) | 63,371 |

Consequences:
- **Reply visibility is better than trap 1 implied, for Apollo-era mail**: prospect
  replies can appear as `[<<]` rows even where no Gmail/Outlook sync ran. Only 18 of 200
  sampled Apollo-inbound rows have an `INCOMING_EMAIL` twin — the two capture routes are
  largely disjoint.
- **Amplemarket inbound does not exist** (981 rows with internal To of 63.4k — under
  inspection, not a systematic inbound log). Trap 1 stands in full for Amplemarket-opened
  pushes: outcomes are "can't see", excluded.
- The **inbound set** for reply detection = external-sender `INCOMING_EMAIL` + external-
  sender Apollo-inbound rows, deduplicated (same sender + normalised subject + close
  timestamps).
- The **outbound touch set** = internal-sender rows that are NOT inbound-logged (mailbox
  sends + Apollo `>>` + Amplemarket sends + CRM_UI).
- Apollo subject prefixes are stripped before any text is read or classified.
- The **rep-month sync check** must count both inbound routes; "any incoming" includes
  Apollo-logged inbound addressed to the rep.

## 3. Misc

- 969 warm-up emails flagged by subject markers; excluded from touches.
- 178 outgoing rows with zero parseable recipient (0.05%) — excluded, counted.
- 135 of 21,340 INCOMING_EMAIL rows have internal senders (internal mail) — excluded.
- direction=EMAIL rows from external domains (axios, gong, github, citypantry…) are the
  Apollo inbox log at work, not a data error.
