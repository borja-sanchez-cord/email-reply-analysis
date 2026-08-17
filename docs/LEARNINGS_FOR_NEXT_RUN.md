# Learnings for the next run — what a fresh agent should be told up front

Written at the end of the v2 study, deliberately in the same spirit as the handoff brief's
"five traps": **facts found the hard way, not conclusions**. Everything here is checked
against this run's own pull. Nothing here says what makes an email get a reply — that is
the study's job, and a fresh run should still find it independently.

---

## Part 1 — Facts about the data that would have saved hours

### 1. There are four internal sending domains, not one

`encord.com`, `encord.ai`, `tryencord.com`, `cord.tech`. The alt domains are **not** just
sequencer infrastructure — reps run real, mailbox-synced outbound from them
(`hs_object_source = EMAIL`: encord.ai 42.5k rows, tryencord.com 22.5k).

Consequence: filter to `@encord.com` and you silently discard about half the corpus.
Sender identity must resolve by **local part across all four domains**
(`hugo@encord.ai` and `hugo@encord.com` are one person). Watch for ambiguous local parts
(`james@tryencord.com` vs three different `james.*` owners) — resolve from evidence or
leave unclassified, never guess.

### 2. Apollo logs the rep's whole inbox into HubSpot as `direction=EMAIL`

This is the single biggest correction to the brief's model of the data.

| pattern (in `hs_email_subject`) | what it is |
|---|---|
| `[Apollo] [Email] [<<] …` or `Email: << …` | Apollo-logged **inbound** |
| `[Apollo] [Email] [>>] …` or `Email: >> …` | Apollo-logged **outbound** |

**74% of all inbound mail in the window (54,363 of 73,856 after dedup) arrives through the
Apollo log, not through `direction = INCOMING_EMAIL`.** Build the inbound set from
`INCOMING_EMAIL` alone and you throw away three-quarters of the replies, then conclude
that everything has a dismal reply rate.

So trap 1 in the brief ("sequencer emails have no replies recorded") needs splitting:

- **Amplemarket**: trap 1 holds in full. No inbound log exists. Those pushes are
  "can't see", and must be excluded, never counted as non-replies.
- **Apollo era**: prospect replies *are* often visible via `[<<]` rows, even without a
  Gmail/Outlook sync. The two capture routes are largely disjoint — only 18 of 200 sampled
  Apollo-inbound rows had an `INCOMING_EMAIL` twin — so both must be pulled and then
  deduplicated (sender + normalised subject + timestamp bucket).

Corollary that looks like a data bug and is not: `direction = EMAIL` rows from
axios.com, gong.io, github.com, notifications.hubspot.com are the Apollo inbox log at
work. Strip the Apollo subject prefixes before any text is read or classified.

### 3. "CA" means Commercial Associate, and team membership is wrong in both directions

CAs frequently sign with cover titles — "AI // ML // Computer Vision", "GTM",
"ML Partnerships" — so a title-based rule alone also fails.

Using HubSpot team membership alone (the brief's suggested route) gets it wrong **both
ways** in this data:

- **7 team-CAs are not doing CA work**: Head of Sales, Head of Physical AI, a Customer
  Success Manager, a Strategic Account Manager, Account Executives. Their mail is
  existing-customer and leadership correspondence.
- **17 CAs are invisible to the team lists**: departed reps whose owner records are
  archived and teamless, but whose sending behaviour is unmistakably CA outbound.
- **The single largest sender in the whole corpus (10,304 clean openers) is Marketing.**
  Leave them in and mass webinar blasts dominate anything you compute about "cold email".

What worked: three independent evidence streams — (a) team membership, (b) role lines
extracted from the senders' own signatures, (c) blind style-reading of 8 random emails per
sender by an agent that saw no outcome. Where they disagree, behaviour wins, and the
decision is documented per sender.

### 4. The gap distribution has no clean trough

Expect this shape, not bimodality: a dense 0–14 day cluster (80% of all gaps), then a
**distinct secondary bump at 27–29 days** (monthly-cadence follow-ups — scheduled steps of
the same outreach, not new pushes), a local minimum at 30–32 days, then a flat tail with
no further structure. Cut *after* the monthly bump. Re-run at one shorter and one longer
value regardless; the choice is a judgment call, not a discovery.

### 5. Field facts worth knowing before choosing a field list

- `hs_in_reply_to_engagement_id` — **0% filled**, both directions, all months. Unusable.
- `hubspot_owner_id` — only 55–84% filled on outgoing. Sender attribution **must** fall
  back to `hs_email_from_email`.
- `hs_email_thread_id`, `hs_email_message_id`, `hs_email_logged_from`,
  `hs_incoming_email_is_out_of_office` are **mailbox-only** fields. Their outgoing fill
  rate falls 71% → 35% → 5% across the window. That is the sequencer ramp, **not** a
  decline in data quality — do not read it as one.
- `hs_object_source` (`EMAIL` = mailbox, `INTEGRATION` = sequencer) is 100% filled and is
  the load-bearing split for the whole study.
- Confirmed empty, as the brief said: both persona fields. Actual fill rates on our pull:
  jobtitle 92%, `job_seniority` 68%, `seniority` 33%, country 98%, company 99%.

### 6. Calendar accept/decline notices are ~12% of reply candidates

Machine "Accepted:" / "Declined:" notices. Counting them as human replies would inflate
reply rates substantially. They need their own category in the reply classifier.

---

## Part 2 — Traps beyond the five in the brief

### 7. Five specific counter defects, all silent, all plausible-looking

Each of these produced a believable number that was wrong. The brief mandates the
"print 20 examples" audit; this is what it actually catches:

1. **Tracking URLs counted as questions.** `…/webinar/x/?utm_source=…` ends a segment with
   `?`. Emails "with a question" were 72% before the fix, 55% after. The same URLs added
   30–80 words each to word counts.
2. **Unsubscribe and legal-confidentiality footers surviving the signature split**, adding
   a question and ~60 words to every email carrying them.
3. **Hard-wrapped plaintext.** Gmail/Outlook wrap at ~72 chars, so splitting on newlines
   counts *lines* as sentences and truncates questions at the wrap point (questions
   recorded as `'coffee?'`). This is a systematic **plaintext-vs-HTML** difference — i.e.
   a difference between mail clients masquerading as a difference between writing styles.
   Unwrap paragraphs before measuring anything.
4. **Signature logos and bold job titles counted as body formatting.** Parsing formatting
   over the whole HTML gave `has_bold` = 77% and images on 75% of emails; the bold text
   was `'AI // ML // Computer Vision @ Encord'`. Fix: record the offset of each
   image/bullet/bold run and count only those inside the body region. Result: 33% and 0.1
   images/email.
5. **Short names and companies matching ordinary words.** A contact named "Or" matched the
   word "or"; a company called "Speak" matched the verb. Require ≥3 characters and word
   boundaries; require capitalisation for short single-word company names.

### 8. Blinding leaks — and over-redaction — are both real

- Sender names survived into ~30% of judge items through signature blocks that the
  sign-off detector missed. The judge seeing who wrote the email breaks the study's most
  important rule.
- The `On <date>, <name> <addr> wrote:` quote header frequently **wraps across two or
  three lines**, so a line-by-line regex never matches it and the quoted trail survives.
- Redacting too hard is equally damaging: an owner surnamed *Short* turned "a short call"
  into "a [SENDER] call". Prune the redaction vocabulary by **corpus frequency** (drop
  tokens appearing in >2% of emails) rather than by a hand-written stoplist.
- Run an automated leak check (sender names, `@company` addresses, raw URLs, ISO dates,
  `wrote:`) over the built batches **before** launching the judges, not after.

### 9. Agents silently drop items from batches

9 of 209 reply batches returned 77–79 labels for an 80-item input. Because a missing reply
label makes a push look like "no reply", this corrupts the **outcome variable** itself.

Always validate per-batch coverage against the input ids, re-run the gaps, and tell the
agent explicitly to count the input first. Do not trust the agent's self-reported count.

---

## Part 3 — Process

### 10. Time and size budget

Universe pull (~380k emails, Sep 2024 – Jul 2026): ~45 min, monthly chunks with recursive
splitting under the 10k search cap. Associations + contacts + companies: ~30 min. Bodies
for openers and reply candidates: ~15 min. Budget roughly two hours of pure pulling.

**Do not pull all 380k bodies** — several GB for no analytical gain. Pull bodies only for
the openers and the inbound emails that are candidate replies (~78k here).

### 11. Make every stage resumable, and decouple stages

Write one file per chunk/batch and skip-if-exists. Background agent runs **die when the
session is interrupted** (this happened twice in this run); recovery came entirely from
the file system, not from the agents. Resume by diffing input ids against written outputs.

Also: don't let one blind pass depend on another finishing. Judging was initially gated on
the type classifier; decoupling it (judge every eligible CA opener, filter by type at
analysis time) removed a needless serial dependency.

### 12. Build the audit tool on the production pipeline

The first version of the counter audit re-derived text with its own regex, so it disagreed
with what was actually being measured — the audit said one thing and the stored feature
another. The audit must import and call the same functions the features use.

### 13. Run the reply-classifier accuracy check early

It is cheap and it de-risks everything downstream, because that label *is* the outcome.
Two independently-worded passes agreed 99.0% on "a human replied", and all three
disagreements were the same benign pattern (a human sentence inside a machine wrapper).
Knowing that before building the analysis is worth more than knowing it after.

---

## Part 4 — Judgment calls in this run that a fresh run may reasonably make differently

Stated plainly so they can be second-guessed rather than inherited:

1. **G = 30 days.** Defensible from the distribution, but not forced by it. Robustness runs
   at 21 and 45 exist for exactly this reason.
2. **Counting `referral` as "Interested".** Pre-registered before seeing data, but
   arguable — a redirect to a colleague is progress, not interest.
3. **Including 17 behaviourally-identified "fallback CAs".** This roughly doubles the
   corpus (7.4k → 15.6k openers) and is the most consequential single decision in the
   study. Results are reported split by CA class so the choice can be inspected.
4. **Excluding `is_reply_like` openers.** A second safety net beyond the thread check; it
   removes ~4% of "cold pitches" that were really mid-conversation messages whose threads
   carried no `thread_id`. Right call, but it is a model-made judgment on text.
5. **The 2026 holdout is confounded, and this limits what it can settle.** In 2025, 75% of
   pushes were mailbox-opened; in 2026 only 28% (outbound roughly doubled, and the growth
   went to the sequencer). A prediction that fails in 2026 may be failing because the
   sender mix and channel mix changed, not because the writing stopped working. Say which
   explanation can and cannot be ruled out — do not treat the holdout as a clean verdict.

---

## Part 5 — One structural suggestion for the next brief

The brief's instruction "never use agents for pulling, filtering, computing features, or
the analysis itself — one agent, sequential" was correct and worth keeping. The failure
mode it prevents (parallel agents on the same files producing numbers that don't
reconcile) is real.

But it is worth adding the converse: **the classification and judging passes should be
agent work, and they should be treated as instrumentation that needs calibration** — a
second differently-worded pass for reply labels, 20 read examples per assigned type, a 10%
re-score for judged dimensions, and an automated blinding check before any of it runs. In
this study the classifier calibration caught more real problems than the analysis did.

## 13. A gate whose thresholds are relative gives different verdicts on the same bytes

The blinding gate decides whether a name token is really an ordinary English word from
lowercase evidence *inside the corpus it is handed*. Hand it a subset and the thresholds
move: the identical 7,055 texts that were CLEAN inside a 12,462-item corpus came back
BLOCKED on their own (§9.10). Nothing had leaked — `max` and `kit` had simply stopped
clearing the "this is an ordinary word" bar.

Two lessons, and the second is the one that saved time. First: a gate that computes its own
vocabulary from the corpus under test must take that vocabulary from a fixed reference
corpus instead, or it is not a fixed gate. Second: the run-1 fix of **reporting the pruning
decision as a separate reviewable list** is what turned a launch-blocking mystery into a
two-minute read. Build audits so that the judgement calls they make are printed next to
the verdict, never folded into it.
