# Email analysis — what gets a reply

*Study of ~12,000 outbound emails, 2025 → Jul 2026. This is the plain-English write-up;
every number is reproducible from `scripts/` and documented in `docs/`.*

This was a hard study to run honestly: 12,000 emails is enough to find the large effects,
but too small for subtle ones. Where we say "no change" below, it means "no effect big
enough to detect" — not "proven useless."

---

## How we did it

We set out to answer three questions: **what email characteristics lead to replies, what
is the ideal number of follow-ups, and how our outreach changed between 2025 and 2026.**

- We analysed every first-touch email sent by CAs in 2025 and Jan–Jul 2026 — about 12,000 —
  plus their follow-up chains, and matched each one to whether a human replied.
- The outcome is a **human reply, not an SAO**. An SAO sits too far downstream of any single
  email — too much drifts in between for the link to be measurable. A reply is the closest
  outcome the email itself controls.
- Each email was measured in two layers: **countable** features (length, questions, links,
  subject line) and **qualitative rubrics** graded by a blinded AI judge (reason for
  writing now, research depth, ask clarity, and so on). The judge never saw who wrote an
  email, when, or whether it got a reply.
- **Amplemarket mail is excluded**, because its replies cannot be tracked. Apollo mail IS
  included — it sends through the rep's own Gmail, so its replies are visible. The
  exclusion does not distort the findings: sequencer-sent email replies about 2 points
  lower than hand-sent, but that is a flat offset, not a change in what works — of 29
  features tested, only 2 showed any difference in effect by send route, fewer than chance
  would produce. The tool shifts the baseline; it does not change which emails do better.
  (A flat, uniform offset is more consistent with some replies going uncaptured than with
  blasts genuinely persuading less well — the two can't be fully separated.)
- Two guards against fooling ourselves. Every comparison is made **within the same rep**,
  so "templates hurt" cannot secretly be "worse reps use templates." And the headline
  findings were written down as predictions using 2025 data only, then tested once against
  2026 data that had been kept sealed.

---

## 1. Writing style

### What works (each effect holds after controlling for the others)

**1. Mass templates cut replies by 2–4×.** Hand-written cold email replies at 9.3%,
templated at 4.8% (2025). In 2026 the gap is wider: 8.0% vs 1.8%.

Three explanations were on the table, and we tested what we could:

- *Templates lower your ability to personalise — a quality-for-quantity trade-off.* True,
  but it explains only ~13% of the gap. And personalising inside a template does not
  rescue it: a recipient-specific reason earns +6.4 points in a hand-written email and
  roughly nothing in a templated one. Better template copy is not the fix.
- *Prospects can tell it's a template.* Consistent with the strongest clue we have: when
  templated emails do get replies, they arrive in 4.8 days versus 1.8 for hand-written —
  read, then set aside.
- *Reps put templates on the accounts they care less about.* Possible, and impossible to
  separate from the previous explanation without an A/B test.

**2. A "why now" roughly doubles replies — and the layers matter more than the average.**
The working theory the data supports: **applied research beats vague research.** Research
that produces a reason to write *now* works; research that only proves you looked does not.
Reply rate by what the stated reason is about (2025):

| the reason for reaching out | example | replies |
|---|---|---|
| nothing | "Just wanted to reach out" | 3.0% |
| us | "We just raised our Series B" | 3.9% |
| an invite sent to a list | "We're hosting a dinner in London" | 4.5% |
| their industry | "CV teams are struggling with data quality" | 4.9% |
| **them** | "I saw you launched MirrorEye 5th gen" | 7.4% |
| **them — and it's why you're asking** | "…is consolidating your data pipelines front of mind now?" | **13.5%** |

The jump is between "their industry" and "them." Everything above that line earns 3–5%;
naming their actual situation doubles it, and connecting it to the ask takes it to 3.5×.
Note that 96% of cold emails already state *a* reason — most state the "us" kind, which
performs like having none. The bar is not "has a reason"; it is **about them, driving the
ask.**

**3. Under 100 words: 1.8× (2025).** 10.3% vs 5.7%. The benefit is a floor, not a slope —
under 100 helps, but going shorter still (under 60) adds nothing further.

**4. A question as the subject line: 1.8× (2025).** 10.5% vs 6.0%.

Two apparent negatives are counted once, not separately: **bold text** (−4.3 points) and
**re-using the prospect's name mid-body** (−5.4 points) look like findings of their own,
but 77–80% of the emails that do these are templates — they are mostly the template
finding wearing different clothes.

### Tested, no change in replies

Bespoke-looking writing · researching the prospect · mentioning their company · adding
links · greeting by name.

The first two connect to the theory above: what these rubrics captured is mostly the
*vague* kind of research — "impressive work on X" — which flatters but gives no reason to
answer this week. Also worth knowing: links don't hurt. People assume they do; they don't.

### Send volume (found along the way, and large)

A rep's reply rate falls with how much they send in a day: **16.4% on 1–2-email days vs
4.0% on 26+ days.** It holds within the same rep and on hand-typed mail alone, so it is
not an automation artifact. Volume is the price each email pays.

---

## 2. Ideal follow-up cadence: 3 emails

- Email 2 replies nearly as well as email 1 (8% vs 9%).
- Email 3 earns 3–4%.
- Email 4 earns 1–3% — that is where reply rates drop steeply.
- The raw data said ~4% forever, but that came from reps chasing only their favourites. In
  automated sequences, where every silent prospect gets the next email, the email-4 drop
  is visible.

---

## 3. How outreach changed, 2025 → 2026

The point of this section: things did not just get worse because of sloppier writing —
the *how* changed.

1. **Total volume nearly doubled** (8,300 → 15,300 sends per month).
2. **Hand-sent email fell from 73% to 24% of sends** — sequencers took over.
3. **Emails got shorter**: half are now under 100 words; it was a quarter.
4. **The clear "why now" — the thing that works — dropped from 71% to 54%** of cold
   emails.
5. **Reply rate on trackable mail held flat: 6.9% → 6.5%.** The blended rate fell for a
   different reason: Amplemarket tripled the volume of mail whose replies we cannot see,
   and the flood grew faster than the replies. The same pattern shows per rep — the
   heaviest daily senders have the lowest per-email rates.

---

## Limits, and what would come next

- This is our own history, not an experiment. The two headline findings — templates and
  why-now — were predicted in advance and held on sealed 2026 data. The rest is strongly
  indicated, not proven.
- Ideally we would study every token — word order, paragraph order, phrasing. The corpus
  is too small for that.
- These findings could drive a coaching agent that checks drafts, but Goodhart's law
  applies: reward "mentions a reason" and you get generic reasons, which are worth
  nothing. A coach has to hold the real bar — the reason is about the recipient and
  drives the ask — and even that can be gamed by invented specifics, which no text
  analysis can detect. The safety net is an A/B test on the two proven levers.

---

*Full technical record: `docs/00`–`docs/19` (methodology, audits, corrections, dead ends),
`rules/` (pre-registered analysis plan), `scripts/` (every step, reproducible).*
