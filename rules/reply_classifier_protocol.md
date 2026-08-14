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

---

# Addendum: the forward-motion boundary (2026-08-14)

**Appended, not edited.** The original protocol above stands unchanged; the git history is
the proof that it was written before any reply was read. This addendum exists because the
§1b accuracy gate FAILED and diagnosed exactly why.

## Why this addendum exists

`docs/11_intent_accuracy_gate.md`: two independently-worded passes over 300 replies agreed
on Interested only **83.3%**, against a pre-registered gate of 90%. The failure was not
spread across the taxonomy. All eight real intents agreed at **96.2%**. The `other_human`
catch-all — 39% of the sample — agreed at **62.9%**. Resolve `other_human` and the gate
reads 97.7%.

`other_human` was never defined. It was the bucket for "human, but none of the above", and
two careful readers split it differently. That is a **definition defect, not an accuracy
defect**, and it is fixed by writing the boundary down, not by tuning a classifier.

## The four rulings

Decided by the operator on the four ambiguous shapes actually observed in the disputed
replies. Each is stated with the case that produced it.

| # | Shape | Ruling | Real example |
|---|---|---|---|
| 1 | **Loops in a colleague** — names or CCs someone else as the right person, or asks for them to be added | **INTERESTED** — record as `referral` | *"Please add Ravi Lambi to the invite as well."* |
| 2 | **A concrete commercial or technical next step** — NDA signed, users to provision, POC data handed over, contract to counter-sign, pricing requested | **INTERESTED** — record as `wants_materials` unless a call is proposed, in which case `wants_call` | *"We received the signed NDA today… create everyone copied as platform users."* |
| 3 | **A question inside a refusal** — declines, but asks something in passing | **NOT INTERESTED** — the refusal governs. Record as `not_interested`, or `not_now` if a door is explicitly left open | *"This dinner is in London? I'll be in the states so can't make it, but I appreciate the invite!"* |
| 4 | **Bare acknowledgement** — reads and responds, asks for nothing, offers nothing actionable | **NOT INTERESTED** — record as `other_human` | *"Thanks, noted."* / *"Got it."* |

## The general rule these four express

> A reply is **Interested** when it hands the sender something concrete to do next: a
> meeting to take, a question to answer, a document to send, or a named person to contact.
> It is **not** Interested when the sender's only available next action is to try again
> later, or nothing at all.

`other_human` is now explicitly the **residual for human replies that create no next step**
— acknowledgements, pleasantries, off-topic remarks, unclassifiable text. It is no longer a
dumping ground for anything the taxonomy did not anticipate. A reply that creates a next
step must be assigned the intent describing that step.

## Two things this addendum must not do

1. **It must not tune pass A until it agrees with pass B.** Pass B has its own errors — it
   read ruling 3's example as `asks_for_information` purely because of the question mark.
   Agreement with a second imperfect instrument is not accuracy.
2. **It must not redefine `interested` to make the gate pass.** The Interested SET is
   unchanged: `wants_call`, `asks_question`, `wants_materials`, `referral`
   (`RUN2_PREREGISTRATION` §1, operator-confirmed). This addendum sharpens which replies
   land in which intent — it does not move the finish line.

## How it is applied and re-measured

- **Scope: the 4,030 `other_human` replies only** (~51 Fable batches). The other 6,927 human
  replies are not relabelled — their intents agree at 96.2% and there is no defect to fix.
  Operator-confirmed scope.
- Same model (Fable) and same blinding as the original pass: reply text only, quoted trails
  stripped, no sight of the outgoing email, sender, date or outcome.
- **Re-measured on a FRESH SEED.** Re-running the gate on seed 20260814 would measure the
  tuning, not the classifier. A new sample is drawn, pass B is re-run on it, and the gate
  must clear 90% on replies never used to write these rules.
