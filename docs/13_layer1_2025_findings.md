# Round 1 (Layer 1) findings — 2025, committed before 2026 is opened

Run 2026-08-15 per `rules/RUN2_PREREGISTRATION.md` stages 4–5. Everything here is computed
on **2025 openers only**. The 2026 half of the corpus is the holdout
(`rules/eligibility_and_analysis_rules.md` §9): the predictions in the final section are
committed now, and 2026 will be opened **once**, after Round 2 (judged qualities) is also
finished, so the holdout is never read twice.

Method, as pre-registered: for each declared feature (`rules/analysis_splits_addendum.md`),
the reply rate with vs without. The primary estimate is **within-sender** (§3): a linear
probability model with sender fixed effects, standard errors clustered by sender — each rep
compared against their own emails, so rep skill and targeting drop out. Benjamini–Hochberg
across the 24 features per run; q < 0.05 to count. Analysis code:
`scripts/analyze_q1.py`; per-run artefacts `output/q1_*.json`, full tables
`output/q1_stdout_*.txt`.

## Cold pitches, 2025 (n = 5,153; replied 6.9%, interested 4.7%)

Six features pass BH on `replied`. Effects are the within-sender estimates (fe_gap, in
percentage points):

| feature | with | without | FE gap | q | reps same direction |
|---|---|---|---|---|---|
| templated (3+ identical bodies) | 4.8% (n=2,767) | 9.3% | **−5.4pp** | <0.0001 | 10/12 |
| uses their name again in the body | 2.0% (n=395) | 7.3% | **−5.4pp** | 0.0008 | 4/4 |
| short (≤100 words) | 10.3% (n=1,368) | 5.7% | **+4.5pp** | 0.006 | 9/11 |
| subject is a question | 10.5% (n=998) | 6.0% | **+4.5pp** | 0.021 | 7/9 |
| has bold text | 4.1% (n=567) | 7.3% | **−4.3pp** | <0.0001 | 3/3 |
| asks 2+ questions | 5.2% (n=847) | 7.2% | **−2.5pp** | 0.021 | 5/8 |

On `interested` three pass: short ≤100 (+3.3pp, q=0.032), templated (−4.0pp region), has
bold (−3.3pp region) — same directions, smaller outcome. `subject is a question` is +3.9pp
on interested but misses BH (q=0.17).

### The three negative findings are substantially ONE finding

Measured overlap: **77% of bold-text emails and 80% of name-again emails are templated.**
Bold text and a re-used first name mid-body are what mail-merge blasts look like, not
independent sins. Among non-templated emails only, both directions hold (bold 6.0% vs
9.5%; name-again 3.8% vs 9.5%) but on cells of 133 and 79 — directionally consistent,
not independently established. The honest headline is therefore **one phenomenon**:
*mass-produced emails underperform hand-written ones by ~5pp within the same sender*,
with bold text and recycled-name-tokens as its visible fingerprints.
(`asks 2+ questions` is only 34% templated — that one is genuinely separate.)

### Word-count shape supports the split, and it is not "shorter is always better"

<50 words 11.0% · 50–99 10.2% · 100–149 5.5% · 150–249 6.7% (250+ n=1). The fall happens
at ~100 words, exactly where the pre-declared split sits; below 100 there is no extra gain
for being extra short (`very short ≤60` is not significant).

### Notable nulls, named so they cannot be quietly forgotten

- **Links do not hurt.** Direction is positive (has a link: 12.6% vs 6.5% pooled; FE
  +4.9pp, q=0.098) — suggestive, fails BH. The "never put links in cold email" folk rule
  finds no support here.
- **Greeting them by name: nothing** (FE −2.1pp, q=0.31 — if anything, negative).
- **Mentioning their company: nothing** (FE −0.0pp). Name-dropping is not personalisation.
- Subject length, sentence/paragraph counts, images, informal greeting: all null.

## Event invites, 2025 (n = 3,179; replied 15.1%)

| feature | FE gap | q | note |
|---|---|---|---|
| has bullets | **−9.6pp** | <0.0001 | 4/4 reps negative; agenda-style formatted invites |
| templated (3+ identical) | **−10.1pp** | 0.013 | 8/8 reps negative — same story as cold pitch |
| short (≤100 words) | **+17.5pp** | 0.027 | 4/5 reps |
| mentions their company | +3.3pp | <0.0001 | pooled gap only +1.0pp; FE-only effect — treat with care |
| informal greeting (hey) | +19.3pp | 0.021 | n=77, one rep — **flagged, small cell** |
| no greeting | +21.2pp | 0.021 | n=72, one rep — **flagged, small cell** |

The two greeting findings sit exactly in the small-cell class the placebo flagged as
fragile (below); they are recorded but carry no weight until 2026 says otherwise.
`interested` on event invites: **0 of 18 significant.**

`other` (n=168) and `post_event_followup` (n=91): too small, counts reported only.

## Question 2 — the follow-up curve, 2025, corrected matching (§9.5)

Re-run because the committed curve predated the defect-7 fix and pooled 2026.
All types, 8,591 pushes (`output/q2_curve_all_2025_G30.csv`; mailbox-only variant agrees):

| touch | got it | replied after it | conditional rate |
|---|---|---|---|
| 1 | 8,591 | 352 | 4.1% |
| 2 | 6,630 | 334 | **5.0%** |
| 3 | 3,505 | 125 | 3.6% |
| 4 | 1,178 | 39 | 3.3% |
| 5–8 | 605→115 | 52 | 3.5–5.7% |

Cumulative: 4.1% → 8.0% → 9.4% → 9.9% → … → 10.5% by touch 8.

Plain reading: **the first follow-up is worth as much as the opener** (5.0% vs 4.1% —
actually slightly more), touch 3 still adds ~1.4pp cumulative, and everything after touch 4
adds ~0.6pp combined. 61% of all eventual replies arrive after the opener. The per-touch
rate never collapses — but the pre-registered selection caveat stands: who receives touch 5
is the rep's choice, so late-touch rates describe survivors, not what touch 5 would do to a
random contact.

## Verification (all pre-registered)

- **Placebo (§5.2): PASS.** Outcomes shuffled within sender, 5 seeds × 2 outcomes =
  240 shuffled tests through the identical code path: 5 spurious BH hits (2.1%, under the
  ~5% ceiling), scattered across seeds and features, both directions, no real finding
  reappearing. The spurious hits concentrated in small-cell features — hence the small-cell
  flags above.
- **G-robustness: PASS.** All 6 `replied` findings stay BH-significant at G21 and G45 with
  effect sizes within ±0.6pp of G30. On `interested`, short ≤100 dips to q=0.064 at G45
  (same size and direction).
- **ca_class split (§3): consistent.** All 6 features keep the same sign in confirmed-CA
  and fallback-CA subsets; significance splits with the halved samples, no sign flips.

## Limitations

1. **Observational.** Within-sender FE removes rep-level skill, not within-rep targeting —
   a rep may hand-write to the prospects they already believe in. The templated/bespoke gap
   is an upper bound on any causal effect.
2. **Univariate.** Each feature tested alone, and the negative trio overlaps heavily
   (above). No multivariable model was pre-registered for Layer 1, so none is run.
3. Small-cell findings (greeting style on invites; name-again's n=395) are fragile by the
   placebo's own evidence.

## Committed predictions for the 2026 holdout

Decision rule, fixed now: a finding **replicates** if the 2026 within-sender estimate has
the same sign; it is **confirmed** if additionally p < 0.05 (uncorrected — 2026 cold pitch
is n≈1,286, a quarter of 2025, so BH-level power is not expected). Predictions:

| # | prediction (2026, cold_pitch, replied) | expectation |
|---|---|---|
| P1 | templated < non-templated | replicate AND confirm |
| P2 | short ≤100 > longer | replicate AND confirm |
| P3 | subject-question > not | replicate |
| P4 | bold < non-bold | replicate (mostly P1 in disguise) |
| P5 | name-again < not | replicate (mostly P1 in disguise) |
| P6 | asks 2+ questions < fewer | replicate — weakest, held loosely |
| P7 | event invites: bullets−, templated−, short+ | all three replicate |
| P8 | Q2: conditional reply rate at touch 2 within ±2pp of touch 1; ≥85% of cumulative replies by touch 4 | holds |
| P9 | `interested` mirrors `replied` directions on P1–P3 | replicate |

2026 is opened once, for these and the Round-2 predictions together, after Layer 2 is
complete on 2025.
