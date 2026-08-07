# Pre-registered rules: which emails count, and how they will be analysed

**Status: committed BEFORE any eligibility filtering, reply classification, feature
computation or analysis was run.** The git timestamp of this file is the proof. At the time
of this commit, the only data operations performed were: (a) the property-catalogue probe,
(b) a 1,800-email fill-rate probe used solely to choose pull fields, and (c) the raw pull
itself (in progress). No reply rates, no gap distributions, no feature values had been
computed or seen.

Where a rule needs a number that must come from the data (the fresh-push gap), the
*procedure* for finding it is pre-registered here, and the number is reported with a
robustness check. Everything else is fixed in advance.

---

## 1. Unit of analysis

One row per **first email of a fresh outreach push** to a person. Not one row per person,
and not "first email ever received".

A fresh push starts when **nobody — rep or sequencer — has emailed that person for at
least G days**. The first email after such a silence is the opener and is the only email
whose content is scored. G is found from the data as follows (pre-registered procedure):

1. For every recipient, compute time gaps between consecutive outgoing emails to them
   (any sender, any channel — sequencer sends count as touches).
2. Plot the distribution of gaps. Expect a dense cluster inside the first few days (bumps
   and sequence steps) and a wide spread beyond (new pushes).
3. Cut at the trough between the two, expected somewhere around 14–30 days. Report the
   chosen G and the shape of the distribution.
4. Re-run the entire opener-selection and headline analyses at one shorter and one longer
   value (chosen as the nearest round candidates on each side, e.g. G−7 to G−14 and G+14).
   Findings that flip with G are reported as unstable.

## 2. Exclusions (regardless of gap)

- Threads the **prospect started** (first message in thread is incoming).
- **Recaps / scheduling / out-of-office threads**: openers whose content is meeting
  logistics, a recap of a call, or a reply into an OOO exchange. Detected in the type-
  classification step; anything ambiguous goes to "other", never force-classified.
- **Bounced** sends (bounce field or bounce-classified incoming).
- Warm-up traffic (subject markers for mail-warming tools), internal mail (both sides on
  company domains), and emails with no usable recipient address.

## 3. Sender eligibility: CAs only

- Owners are pulled (active + archived) and every distinct team name printed and reviewed.
  CA teams follow `<vertical> <region> CA(s)`. Sales/SE/Marketing/CS teams are not CAs.
- Attribution: `hubspot_owner_id` where present, else match `hs_email_from_email` to owner
  email addresses.
- Owners with no team recorded: first check whether they are archived accounts; report the
  share of otherwise-eligible openers whose sender cannot be classified. If exclusion would
  discard most of the corpus, a documented fallback identification (e.g. senders whose
  observed behaviour is high-volume first-touch outbound) may be used, and results are then
  reported for confirmed-CA and fallback-CA separately.
- Known limitation, stated in the report: team membership is as of today, not as of send
  time.

## 4. Opener channel: rep's own mailbox only

- An opener counts only if `hs_object_source = "EMAIL"` (mailbox sync). If a push opens
  with a sequencer send (`hs_object_source = "INTEGRATION"`, detail Apollo/Amplemarket) the
  entire push is excluded from Question 1 — sequencer replies are structurally invisible in
  HubSpot (verified in the previous data pull: 0 replies recorded across 218,764 sequencer
  sends), so those emails' outcomes are "can't see", never "no reply".
- Sequencer sends still count as timeline touches: they close gaps (no fresh push soon
  after a sequencer touch) and they count in Question 2's follow-up totals.
- The share of pushes opening from mailbox vs sequencer is reported near the top of the
  write-up.

## 5. Email types, analysed separately and never pooled

Types: **cold pitch**, **event invite**, **post-event follow-up**, **other**. Classified
from subject + body; 20 examples per type are read before the classifier is trusted;
anything not confidently classifiable stays "other". Within post-event follow-ups, timing
(days since event) is tested if the group is large enough; if not, that is said plainly.

## 6. Outcome definition

- **Replied** = a real human wrote back in the same thread (or, where thread ids are
  missing, from the recipient's address to the sender) within **90 days** of the opener and
  before the next fresh push to that person. Auto-replies, out-of-office, bounces, and
  unsubscribe-bot messages do not count.
- **Interested** = the human reply moves the conversation forward: asks a question,
  requests materials, suggests or accepts a call. Negative interest ("not interested",
  "unsubscribe") is Replied but not Interested.
- Replies are classified **from the reply text alone** — the classifier never sees the
  outgoing email that prompted the reply.
- Accuracy check (pre-registered): 300 random incoming emails get a second, differently
  worded classification pass ("describe what this email is and what produced it", label
  derived from the description). Agreement rate and the direction of disagreements are
  reported. If agreement is poor, the classifier is fixed and re-measured before use.

## 7. Sync check (before any analysis)

For each rep × month, check whether *any* incoming email is attached anywhere in their
mail. Rep-months with none are dropped from Question 1 (their zero-reply record is
indistinguishable from a dead mailbox sync), and the number of openers removed is reported.

## 8. Feature measurement

- **Computed features** (floor list, more may be added): word count; sentence count;
  paragraph count; contains a real question, how many, question length; links count;
  bullets; bold; images; subject length; subject is a question; mentions recipient's first
  name beyond the greeting; mentions their company; mentions their role; greeting style;
  sign-off style; repeated-template detection (strip personalisation, hash body, count
  repeats — with segment sizes equalised before any cross-segment comparison, per trap 5).
- **Audit rule**: for every counter, print 20 flagged examples and read them before use.
- **AI-judged features**: the rubric is chosen only after reading a few hundred actual
  openers, then written down and committed before any scoring. Judges see the email with
  names, companies, links and signatures stripped, and never see outcome, sender or date.
  A random 10% is re-scored; ratings with poor repeatability are flagged and conclusions
  built on them are downgraded.

## 9. Analysis plan (Question 1)

For each feature: reply rate with vs without (binary features; judged scales are split at
a pre-declared point — top-2-box vs rest for 1–5 scales, or the scale's natural yes/no),
the gap in percentage points, and a rough uncertainty range for the gap (95% two-proportion
interval, reported in plain words). Development set: **openers dated Jan–Dec 2025**.

Checks on anything that looks real:
1. **Within-rep**: among reps with ≥20 openers of both kinds, does the direction hold?
   Reported as "X of Y reps".
2. **Holdout**: findings expected to survive are written down and committed before
   Jan–Jul 2026 openers are examined; then tested there.

Labels: **strong** = held both checks; **mixed** = held one; **weak** = held neither.
Everything tested is reported, including null results. Correlated features are reported
together with the overlap stated. No causal language anywhere: "linked to", never "caused".

## 10. Question 2 (follow-up curve)

Among people who did not reply to email N of a push, what share replied to email N+1?
Email touches only (sequencer sends count; calls/LinkedIn do not, and the write-up says
so). Reported with the pre-registered caveat that reps choose whom to keep chasing, so the
curve is **suggestive only** — it cannot separate "the extra email worked" from "reps kept
chasing the promising ones".

## 11. Reporting rules

Percentages, not statistics vocabulary; limits stated up front; shaky findings labelled
"this is suggestive, not solid" in those words; "we couldn't tell" is a reportable result.
