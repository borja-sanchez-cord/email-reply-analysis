# What makes a first cold email get a reply

You are running a study from scratch. Everything here is either a rule to follow or a checked fact
about the data. No previous study's conclusions appear here, deliberately.

Write plainly throughout. The people reading your output are sales leaders, not statisticians.
Report everything as percentages — "replied 11% of the time versus 8%" — and keep technical
measures out of the main text.

---

## The two questions

1. **On the first email, what leads to a reply?**
2. **How many follow-ups were needed before a reply came?**

That's the whole brief. Nothing else is a deliverable.

**What's out of scope:** what the follow-up emails *said*. We count them; we never read them. The
data set is openers only.

---

## The study in eight steps

1. Pull emails from HubSpot, Sep 2024 → Jul 2026.
2. Keep only: sent by a CA, from their own mailbox, and the first email of a fresh push.
3. Split cold pitches from event invites. Analyse separately, never pooled.
4. For each email: did a real human reply?
5. For each email, measure things two ways — computed by code, and judged by an AI reader.
6. **The judge never sees whether the email got a reply.** This is the rule that matters most.
7. For each thing measured: reply rate with it versus without. Check the good ones hold in 2026.
8. Write it up in plain English.

The rest of this document is detail on each step.

---

## Setup

- **Work in the folder containing this file.** Create everything here. Set up git here.
- **The HubSpot key** is in `.env` in this same folder. Read it from there and nowhere else. Never
  print it or copy it into any file. Add `.env` to `.gitignore` before your first commit.
- **HubSpot is read-only.** Never call anything that creates, updates or deletes.
- **`/Users/borja/builds/CA_central/` is completely off limits.**

### Don't read the old study

A previous study lives in `/Users/borja/builds/email_analysis/`. Reading its conclusions first is
how its mistakes get copied into yours. **Treat that whole folder as off limits**, including
`data/` and `data26/` — you're pulling your own data.

The one exception: `/Users/borja/builds/email_analysis/scripts/` contains pulling machinery worth
reusing. You may open only `backfill.py`, `backfill_2026.py`, `hs_common.py`, `universe_2024h2.py`
and `negatives_fetch.py`. Nothing else in that folder.

Comparing your results against the old study afterwards is fine. Not before.

---

## Step 1 — Pull the data yourself

Pull everything fresh. Don't reuse the old study's files: its field list was chosen for a different
question, and some of its files were built by splitting contacts on the outcome, which would
quietly bias you.

**Ask HubSpot which properties exist on the email object and choose your own fields.** Don't copy
the old scripts' list.

**What to pull:** every email, incoming and outgoing, **1 Sep 2024 → 31 Jul 2026** — around 380,000
records, roughly ten minutes. Plus email bodies (a separate call), the links between emails and
contacts (also separate), and contacts, companies and owners.

The study itself starts Jan 2025. Sep–Dec 2024 exists only so the gap rule in step 2 can be applied
to January emails.

**Two practical notes.** The search endpoint caps around 10,000 results, so date ranges must be
split into chunks and oversized chunks split again — the old scripts already solve this. And the
"to" field is semicolon-separated with display names in it (`Jane Smith <jane@co.com>;...`), so
parse it properly.

Save each chunk to disk as you go, so an interrupted pull resumes rather than restarting.

**Re-check the numbers in this document against your own pull.** Several figures below come from
earlier pulls. If yours differ, yours are right — report what you actually find.

---

## Step 2 — Which emails count

Write these rules down and **commit them to git before looking at any results.** The commit
timestamp is your proof you set the rules before you saw the answers.

### One row per fresh push, not per person

The unit is the **first email of a new outreach push**. Not the first email that person ever
received — after years of outbound almost nobody is truly untouched, and an unopened sequencer
email from eight months ago isn't something the prospect experienced.

**A new push starts when nobody has emailed that person for a while.** The first email after that
gap is the one you score.

**What the gap is for:** it stops bumps being scored as openers. If a rep emails someone Monday
and again Thursday, that Thursday email is two lines saying "floating this to the top of your
inbox." Score that as a cold email and the results will say short emails work brilliantly — when
really they're just third nudges. This exact kind of mistake killed findings in the last study.

**Find the gap length from the data.** Plot the time between consecutive emails to the same person.
You'll see a dense cluster in the first few days (bumps) and a wider spread beyond (new pushes).
Cut at the trough — probably somewhere around two to four weeks. Report where you cut it, then
re-run at one shorter and one longer value to confirm the answers don't depend on the choice.

Also excluded regardless of gap: recaps, scheduling messages, out-of-office threads, and any thread
the prospect started.

### CAs only

This study is about CA outbound. Emails from AEs, solution engineers, marketing or customer success
are a different genre — different intent, often a warm context — and would contaminate everything.

Owner records carry team names, and CA teams follow the pattern `<vertical> <region> CAs` — e.g.
`Computer Vision UK CAs`, `Regulated US CAs`, `PhysAI US CA`. Teams like `Multimodal UK Sales`,
`US Solution Engineers`, `Marketing Team` and `Customer Success` are not CAs. Pull the owners
yourself, print every distinct team name, and decide from what you see.

**Two problems to handle, not ignore:**

- **Most owners have no team recorded.** In an earlier pull, 184 of 235. Many are probably archived
  accounts — check that first. Then report what share of otherwise-eligible emails came from
  someone you couldn't classify. In an earlier estimate this was large for 2025, so if you simply
  exclude them you may lose most of the corpus. If that happens, find another way to identify CAs
  (for example, whoever actually sends high volumes of first-touch outbound) and document it.
- **Team membership is today's, not 2025's.** Anyone who changed role during the window is labelled
  wrong. Note it as a limitation.

### The opener must come from the rep's own mailbox

Emails sent through Apollo or Amplemarket can't be scored, because their replies don't exist in
HubSpot — see trap 1. If a push opens with a sequencer email, that whole push is out.

**But sequencer emails still count as timeline markers.** They close the gap (if Apollo emailed
someone two weeks ago, a rep's email today isn't a fresh push) and they count in the follow-up
total. We just never read them or measure their replies.

**Report what share of pushes open from a mailbox versus a sequencer.** That tells the reader how
representative the studied emails are, and it belongs near the top of the write-up.

### Split by type

Sort emails into cold pitch, event invite, post-event follow-up, and other. **Report each
separately — never pooled.** Event invites almost certainly get replies at a different rate, and
pooling lets "this was an event invite" masquerade as "this was well written."

Print 20 examples of each type and read them before trusting the classifier. Leave anything you
can't confidently classify in "other" rather than forcing it.

**Within post-event follow-ups, also test timing** — how many days after the event the email went
out. Sent same day, next day, a week later. If there are enough of them to say anything, this is
directly actionable; if there aren't, say so and move on.

### Rough sizes to expect

An earlier estimate, using a 30-day gap, found roughly **4,300** confirmed-CA openers in 2025 and
**3,400** in 2026 H1, plus a large bucket from unclassifiable owners. Treat these as a sanity check
only — if your numbers are wildly different, work out why before continuing.

**Report your actual counts per type early, before spending time on judging.** If a group is very
small, say so and scale back rather than producing confident-looking numbers from a handful of
emails.

---

## Step 3 — What counts as a reply

A **real human writing back**. Not an auto-reply, not an out-of-office, not a bounce.

There are no technical headers marking these, so you have to tell them apart from the text. That
means pulling the bodies of incoming emails.

**Two levels, both reported:**

| Level | Meaning |
|---|---|
| **Replied** | A real human wrote back |
| **Interested** | The reply goes somewhere — asks a question, wants materials, suggests a call |

The second is what the business cares about but there'll be far fewer of them, so expect less
certainty. Watch specifically for things that get more replies but not more interested ones — a
cheeky subject line might reliably earn "who is this?" and nothing else.

**Rules for classifying replies:**

- The classifier sees **only the reply text**, never the original email. Otherwise the thing you're
  measuring influences how you measure it.
- **Check your accuracy, don't just trust it.** Take 300 random incoming emails and label them
  through a second, differently-worded pass — ask "describe what this email is and what produced
  it" rather than "is this an auto-reply", then derive the label from the description. Different
  question, different mistakes. Report how often the two agree, and describe which direction the
  errors go ("mostly two-word human replies mistaken for auto-replies"). If accuracy is poor, fix
  it and re-measure.

This matters more than any other check, because this label *is* the outcome. Get it wrong and every
finding is distorted.

---

## Step 4 — What to measure on each email

Two kinds of thing, both on every email in the corpus.

### Computed by code

Word count, sentence and paragraph count, whether it contains a real question and how many, length
of the question, links, formatting (bullets, bold, images), subject line length and whether the
subject asks something, whether it mentions the person's name, their company, their role, greeting
and sign-off style, and whether the body is a repeated template (strip personalisation, hash the
rest, count repeats).

That list is a floor. Add anything else you can compute reliably.

### Judged by an AI reader

Read a few hundred emails first and decide what's actually worth rating — things like whether it
looks researched, how specific it is, whether the ask is clear, whether the relevance to that
person's job is obvious. **Choose these from what you see in the emails, not from assumptions.**
Write the list down and commit it before scoring.

Then score every email in the corpus against that list.

**Two rules:**

1. **The judge never sees whether the email got a reply**, nor the sender, nor the date. Strip
   names, companies, links and signatures. This is the single most important rule in the study.
2. **Re-score a random 10% a second time** and report how often the two scores match. If a rating
   turns out to be unstable, say so and go easy on any conclusion built on it.

### Audit every counter before using it

For anything you count, print 20 examples of what it flagged and read them. Last time a
question-counter was actually counting the unsubscribe footer ("Is this email not relevant to
you?"), and a bullet-point detector was finding calendar confirmations. Both produced findings that
later collapsed.

---

## Step 5 — The check that comes before any analysis

**Whether a rep's mailbox was syncing varies by rep and by month.** If it wasn't connected, every
email they sent shows zero replies — indistinguishable from a rep who writes badly.

Before calculating anything: for each rep, for each month, check whether *any* incoming email is
attached. Drop rep-months with none, and report how many emails that removed.

---

## Step 6 — The analysis

Keep it simple. For each thing you measured:

**Reply rate with it, versus without it.** Report both percentages, the gap between them, and a
rough range for that gap. Nothing more elaborate than that.

Then two checks on anything that looks real:

1. **Does it hold within individual reps?** Take reps who sent both kinds of email and see whether
   the pattern shows up in their own emails. Report it plainly: "7 of 9 reps show the same
   pattern." This is what stops you concluding "short emails work" when the truth is "the rep who
   writes short emails is good at picking accounts."
2. **Does it hold in 2026?** Work everything out on 2025, write down which findings you expect to
   survive, commit that, and only then look at Jan–Jul 2026.

**Label each finding with one word:** **strong** (held both checks), **mixed** (held one), **weak**
(held neither). Say plainly that weak ones are suggestive, not solid.

**Report everything you tested, including everything that made no difference.** The list of things
that don't matter is as useful as the list that does.

**One honest caveat to state:** if two features travel together — say short emails also tend to ask
a question — you can't tell which is doing the work. Report both and say they overlap.

**When comparing 2025 against 2026, note two things** that could make a finding fail for reasons
unrelated to writing: 2026's emails come from a narrower slice of reps, and total outbound roughly
doubled as Amplemarket ramped from nothing. If a prediction fails, say which explanation you can
and can't rule out.

---

## Question 2 — How many follow-ups were needed

Build this curve: of the people who didn't reply to email 1, what share replied to email 2? Of
those who still didn't, what share replied to email 3? And so on. Sequencer emails count as touches.

That's the honest way to ask whether chasing pays off, and it's all question 2 needs.

**Email touches only.** Don't bring calls, LinkedIn or any other channel into this. Say in the
write-up that the count covers emails only, so nobody reads it as a total contact count.

**One warning.** Don't compare "people who got 5 emails" against "people who got 2." Reps stop
emailing someone once they reply, so the 5-email group is by definition people who ignored the
first four — that comparison measures when reps stopped, not whether chasing works. The curve above
avoids this.

**And one thing that can't be fixed.** Reps also stop when they've decided an account is a dead
end, so the number of emails someone got partly reflects the rep's opinion of them. Whatever you
find, label it **suggestive only** and say plainly that you can't separate "the extra email worked"
from "reps chose to keep chasing the promising ones."

---

## Five traps that will quietly ruin this

Facts about the data, found the hard way. Not conclusions.

**1. Sequencer emails have no replies recorded.** Across 218,764 Apollo and Amplemarket sends: not
one. Replies only reach HubSpot through the rep's Gmail or Outlook sync, and attach only if the
original send also synced. Verified two ways — by thread, and by matching email addresses: of 5,627
people who only ever received sequencer emails, 0.36% ever appear as a reply sender, against 8.62%
for mailbox-only recipients.

So for those emails the answer isn't "nobody replied", it's "we can't see." They must be dropped,
never counted as non-replies. (Their bodies *are* available — that's not why they're excluded.)

**2. The field saying how an email was sent doesn't say who wrote it.** A rep can push a
personalised email through Apollo, or paste a template into Gmail. Never call that field
"automated versus hand-written." Measure templating directly instead.

**3. Never assume a field contains what its name suggests.** Check by reading examples. See step 4.

**4. Check when a field started being filled in.** A field introduced halfway through measures its
own rollout, not reality. Already known unusable: both account-tier fields hold today's values, not
values as of send time; the deal-count field is downstream of the outcome, so circular; both
persona fields are entirely empty. Usable, with fill rates: job title 93–98%, seniority 72%,
employee count ~90% (not the employee-range field, ~10%), industry 77–83%, country ~96%.

**5. Repeated-content detection is sensitive to sample size.** "This body appears 3+ times" is
easier to hit in a big sample. Cut segments to equal size before comparing.

---

## How to use agents

**You may run as many agents in parallel as useful. No budget limit, no agent-count limit.** Don't
ask permission again and don't scale down to be economical.

**Never use agents for:** pulling data, filtering, deduplicating, computing features, or the
analysis itself. One agent, sequential. Parallel agents on the same files produce numbers that
don't reconcile.

**Do use them for:**

- **Judging emails** — batches of ~80, blind to outcome, sender and date. Plus the 10% re-scoring.
- **Classifying replies** — plus the 300-email accuracy check.
- **Attacking your findings** — at least 5 per headline claim, each given a different angle: one
  checks the arithmetic, one looks for another explanation, one questions whether the feature
  measures what it claims, one tests whether it survives dropping the biggest rep, one argues it's
  chance. If most knock it down, the claim is dead. Do this before writing the report.

If you ever cut corners on coverage, say so in the output. Quietly analysing less than you claimed
reads exactly like full coverage.

---

## What to deliver

A short document, plain English, structured on the two questions.

**1. What leads to a reply.** Open with a few sentences a rep could act on. Then the list: for each
thing, reply rate with versus without, the gap, and one word for confidence. Include everything
that made no difference.

**2. How many follow-ups were needed.** The curve, with the caveat that reps chose who to chase.

**Then: what you couldn't answer, and why.**

Rules for the write-up:

- Percentages, not statistics vocabulary.
- **Nothing is "caused by" anything.** This is observation, not an experiment. Say "linked to."
- If a finding is shaky, write **"this is suggestive, not solid"** in those words.
- Report what you actually found, including "we couldn't tell." A clear negative is a real result;
  a confident number you don't trust is worse than nothing.
- Don't produce a gallery of good emails as the main output.
- Put the limits up front, not buried: this covers only emails CAs sent from their own mailbox,
  which is a minority of outbound; reps choose which emails to send that way, so it isn't a random
  sample; and nothing here says what follow-up emails should contain.
