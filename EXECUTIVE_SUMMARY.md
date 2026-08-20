# Executive summary

We studied 12,000 outbound emails to answer three questions. What writing gets replies?
How many follow-ups are worth sending? And how did our outreach change between 2025
and 2026?

This is the short version. The full story is in [REPORT.md](REPORT.md).

---

## 1. What we studied

**The data.** Every first outreach email our CAs sent in 2025 and January to July 2026,
about 12,000 emails, plus their follow-up chains. Each email was matched to one outcome:
did a human being reply to it.

**Why replies and not SAOs.** One email almost never creates an SAO on its own. Too many
other things happen in between, so the link is too weak to measure. A reply is the
closest outcome the email itself controls.

**How each email was measured.** Two layers:

| layer | what it covers |
|---|---|
| countable features | word count, questions, links, bullets, bold text, subject line, greeting style, name reuse, company mention, template reuse |
| graded qualities | reason for writing now, research depth, value specificity, customer proof, pain hypothesis, ask clarity, ask size, bespokeness, polish, brevity, tone, recipient focus |

The graded qualities were scored by an AI judge that read only the email text. It never
saw who wrote the email, when, or whether it got a reply.

**What was excluded.** Amplemarket mail, because its replies cannot be tracked. This is
safe: we checked, and what works in an email does not depend on the tool that sent it.
The exclusion costs coverage, not accuracy.

**Why the numbers can be trusted.** Two protections. First, every comparison is made
within the same rep, so "templates hurt" cannot secretly mean "weaker reps use
templates". Second, the headline findings were written down as predictions using 2025
data only, and then tested once against 2026 data that had been kept sealed.

---

## 2. Finding one: writing style

### What works

**Mass templates cut replies by 2 to 4 times.** A template here means the same body sent
to three or more people.

| year | hand-written | templated |
|---|---|---|
| 2025 | 9.3% | 4.8% |
| 2026 | 8.0% | 1.8% |

Why do templates hurt? Three candidate reasons, and what we found for each:

- Templates leave less room to personalise. True, but it explains only about 13% of the
  gap.
- Prospects can tell it is a template. Consistent with our strongest clue: when templated
  emails do get replies, the reply arrives in 4.8 days on average, against 1.8 days for
  hand-written. The email is read, then set aside.
- Reps put templates on the accounts they care less about. Possible. Our data cannot
  separate this from the previous reason. Only an A/B test can.

One more thing we know: personalising a line inside a template does not fix it. A
recipient-specific reason earns about 6 extra points in a hand-written email and roughly
nothing inside a template.

A note on two features that look harmful on their own: bold text and repeating the
prospect's name in the body. Almost all emails that do these are templates, so they are
the template finding in disguise. We count that penalty once, not three times.

**The reason you give for reaching out is the biggest lever we found.** Reply rate by
what the stated reason is about, on 2025 data:

| the reason is about | example | reply rate |
|---|---|---|
| nothing | "Just wanted to reach out" | 3.0% |
| us | "We just raised our Series B" | 3.9% |
| an event, sent to a list | "We are hosting a dinner in London" | 4.5% |
| their industry | "CV teams are struggling with data quality" | 4.9% |
| them | "I saw you launched MirrorEye 5th gen" | 7.4% |
| them, and it is why you are asking | "I saw you launched MirrorEye 5th gen. Is consolidating your data pipelines front of mind now?" | 13.5% |

The rule this table teaches: the reason has to be about them, and it should drive the
ask. Note that 96% of our cold emails already state some reason. Most state the "about
us" kind, which performs the same as having no reason at all. Applied research works.
Vague research does not.

**Short emails work.** Under 100 words replies at 10.3%, against 5.7% for longer emails
(2025 result, see note below). This is a floor, not a slope: going even shorter, under 60
words, adds nothing further.

**A question as the subject line works.** 10.5% against 6.0% (2025 result, see note
below).

*Note: these two were proven on 2025 data. In 2026 the direction held, but too few such
emails were sent to confirm it again.*

### What makes no difference

Each of these was tested and moved replies by nothing we could detect:

- bespoke-looking writing
- researching the prospect
- mentioning their company
- adding links
- greeting them by name

The first two connect to the rule above. What these measure is mostly the vague kind of
research, such as "impressive work on X". It flatters, but it gives the reader no reason
to answer this week. And one piece of folklore to retire: links do not hurt.

---

## 3. Finding two: the ideal follow-up cadence is 3 emails

Of the prospects who are still silent when each email goes out, this is the share that
replies to it:

| email | share who reply |
|---|---|
| 1 (the cold email) | 9% |
| 2 | 8% |
| 3 | 3 to 4% |
| 4 | 1 to 3% |

Email 2 is almost as effective as email 1. Email 3 still earns its keep. Email 4 is
where reply rates drop steeply.

One trap in the raw data is worth explaining. Taken at face value, it says every email
after the third still earns about 4% forever. But reps only kept emailing the prospects
they had a good feeling about, which inflates the later numbers. In automated sequences,
where every silent prospect gets the next email regardless, the drop at email 4 is
clearly visible.

---

## 4. Finding three: how outreach changed from 2025 to 2026

| what changed | 2025 | 2026 |
|---|---|---|
| total send volume, per month | 8,300 | 15,300 |
| hand-sent share of all mail | 73% | 24% |
| cold emails under 100 words | 25% | 50% |
| cold emails with a clear "why now" | 71% | 54% |
| reply rate on trackable mail | 6.9% | 6.5% |

Volume nearly doubled and moved from hand-sent Gmail to sequencer tools. Emails got
shorter, which is good. The one thing that reliably works, a clear reason for writing
now, became rarer. That is the wrong trade.

The last row needs one sentence of explanation. On the mail whose replies we can track,
the reply rate held flat. The blended reply rate across everything fell, but for a
different reason: the volume of untrackable mail tripled, and the flood grew faster than
the replies. The same pattern shows inside our own data: on days a rep sends 1 or 2
emails, 16.4% get replies; on days they send 26 or more, 4.0% do.

---

## 5. What we would do next

- **A/B test the two proven levers.** Same email as a template for half the list and
  typed for the other half. Forced 4th and 5th emails for half the silent prospects.
  These are the only ways to turn "strongly indicated" into "proven".
- **Study the writing at the word level** (word order, paragraph order). The current
  corpus is too small for that.
- **A coaching agent could check drafts against these findings**, with one warning.
  Goodhart's law applies: reward "mentions a reason" and you will get generic reasons,
  which are worth nothing. The bar the agent must hold is the real one: the reason is
  about the recipient, and it drives the ask.

---

*Full write-up: [REPORT.md](REPORT.md). Complete technical record: `docs/`, `rules/`,
`scripts/`.*
