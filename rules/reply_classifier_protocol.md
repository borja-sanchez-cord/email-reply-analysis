# Reply classifier protocol — pre-registered before any reply was classified

## Blinding

The classifier sees **only the cleaned text of the incoming email**: quoted trails
("On … wrote:", "-----Original Message-----", "From:/Sent:" blocks, "> " lines) are
stripped first, because the quoted trail *is* the outgoing email and the rule is that the
thing being measured never influences how it is measured. No sender name, no date, no
subject of the outgoing email, no information about the push. The incoming subject line is
shown (it is part of the reply), after stripping "Re:" prefixes changes nothing either way.

## Labels

Category (exactly one):

| category | meaning |
|---|---|
| `human` | a real person wrote this, by hand |
| `out_of_office` | autoresponder: away, parental leave, "no longer with company" auto-notices |
| `auto_ack` | automated acknowledgement (ticket opened, "we received your message") |
| `bounce_dsn` | delivery failure / mailer-daemon |
| `unsubscribe_bot` | list-unsubscribe confirmations, preference-centre bots |
| `calendar_bot` | calendar/scheduling machine output (invite accepted, Calendly notice) |
| `security_scan` | link-scanner / mail-gateway artefacts |
| `other_bot` | automated, none of the above |
| `unclear` | genuinely can't tell (reported, never silently forced) |

If `human`, intent (exactly one):

| intent | meaning | counts as **Interested**? |
|---|---|---|
| `wants_call` | suggests/accepts a call or meeting | yes |
| `asks_question` | asks a substantive question about the product/offer | yes |
| `wants_materials` | asks for docs, pricing, more info | yes |
| `referral` | redirects to a colleague who owns the area | yes |
| `not_now` | polite deferral ("try me next quarter") | no |
| `not_interested` | declines | no |
| `unsubscribe_request` | human asking to stop emailing | no |
| `who_is_this` | confused/curious reply with no forward motion | no |
| `other_human` | anything else human | no |

**Replied** = category `human`. **Interested** = intents marked yes above.
`referral` counts as interested because the conversation moves to the right person; this
choice is fixed here, before any data was seen, and reported in the write-up.

## Mechanics

- Agents classify batches of ~80 replies; each returns structured JSON per reply.
- Model never told reply rates, hypotheses, or what outcome is "hoped for".
- The HubSpot `hs_incoming_email_is_out_of_office` flag is NOT shown to the classifier;
  it is compared against the classifier's `out_of_office` output afterwards as a cross-check.

## Accuracy check (pre-registered)

300 random reply-candidates get a second pass, worded differently: "Describe what this
email is and what kind of process produced it (a person typing, an autoresponder, a mail
server, a scheduling tool…). Then state what the writer wants, if anything." Labels are
derived from the description by a separate mapping step. Agreement is reported per
category, with the direction of disagreements described. If Replied-level agreement is
below 90%, the classifier is revised and re-measured before any analysis uses it.

## Tie-breaks

- Auto-generated text with a human sentence appended → `human` (the human sentence wins).
- Assistant/EA replying on the prospect's behalf → `human` (a real person engaged), intent
  judged from what the assistant says.
- Forwarded-to-colleague with commentary visible → `human` + `referral`.
- One-word replies ("Thanks", "Received") → `human`, `other_human` unless clearly templated
  gateway text.
