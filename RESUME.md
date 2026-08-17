# Resume here

Written 2026-08-14 mid-run, because the session window was about to close and
background agent runs die when the session is interrupted
(`docs/LEARNINGS_FOR_NEXT_RUN.md` #11). Recovery is from the filesystem, never
from what an agent reported.

## Read first

1. `rules/RUN2_PREREGISTRATION.md` — the whole plan. **§9 is the correction log and
   overrides §8.3 on the facts.**
2. This file.

## The one-line state

**Round 1 is COMPLETE and committed** (2026-08-15): rubric middle anchors written first,
then Layer 1 on 2025 only, placebo PASS (2.1% vs 5% ceiling), G21/G45 robustness PASS,
ca-split consistent, Q2 curve re-run on corrected matching, 2026 predictions committed in
`docs/13_layer1_2025_findings.md`. Headline: templating −5.4pp, short ≤100 +4.5pp,
subject-question +4.5pp, all within-sender. **2026 has NOT been opened** — it opens once,
after Round 2. Next step: judging (build batches → check_blinding → 20-example read →
launch, ~$110). No email has been judged yet.

## The intent gate — RESOLVED, do not re-open

Failed at 83.3%, diagnosed as one undefined bucket, fixed, re-measured at **92.8%** on a
fresh seed (77771) excluding every reply used to write the rulings. Full account in
`docs/11_intent_accuracy_gate.md`. Both the failure and the resolution are reported.

What was done: five operator rulings appended to `rules/reply_classifier_protocol.md`;
677 study-linked `other_human` replies relabelled on Sonnet; a 240-reply reverse check
(97.5% stayed interested vs 62.3% moving in — 25:1 asymmetry) confirming the correction is
real and not model drift. `interested` 6.0% → 6.9%.

## Exactly where to pick up

### Step 0 — confirm nothing regressed

```bash
cd /Users/borja/builds/v2_email_replies_analysis
.venv/bin/python -m pytest tests/ -q                 # must be 43 passed
ls output/type_labels | wc -l                        # must be 485
```

Then check the numbers table above. All of stage 0/1 and the frame rebuild is done;
labelling agents do **not** need re-running.

### Round 1 — DONE 2026-08-15, do not redo

1. ~~Rubric middle anchors~~ — committed before Layer 1 ran (`rules/judge_rubric.md`).
2. ~~Layer 1 on 2025~~ — `output/q1_*.json`, `output/q1_stdout_*.txt`. analyze_q1.py now
   implements the §3 primary spec (sender FE, cluster-robust SEs) + BH + `--ca` split +
   `--shuffle-seed` placebo.
3. ~~Placebo~~ — 5 hits / 240 shuffled tests (2.1%), PASS.
4. ~~Q2 re-run~~ — 2025 only (holdout), `output/q2_curve_all_2025_G30.csv`.
5. ~~Findings + predictions committed~~ — `docs/13_layer1_2025_findings.md` (P1–P9).

### Round 2 — DONE 2026-08-15, do not redo

1. ~~Judge batches~~ — six blinding defects found by READING items (§9.7), gate rebuilt,
   0 leaks across 12,462 items. Corpus tied to the frame union (§9.8).
2. ~~Judging~~ — 312 Sonnet batches + gap-fills; every id verified from disk;
   `data/judge_scores.parquet` (12,462 rows, hard invariants in
   `scripts/assemble_judge_scores.py`).
3. ~~Validation~~ — halo PASS (mean |r| .188, PC1 28.4%); repeatability by top-2-box
   kappa: `economy` .22 and `peer_tone` .32 FLAGGED, Fable-vs-Sonnet gap −0.016
   (ambiguous questions, not a weak model). `scripts/judge_agreement.py`.
4. ~~Layer-2 analysis on 2025~~ — `docs/14_layer2_2025_findings.md`. Headline:
   `why_now` +4.6pp (q<1e-4, 10/11 reps, survives length control);
   research_signal/bespokeness/ask_clarity NULL; recipient_centricity +5.3pp
   exploratory; length control kills pain/proof-industry negatives.
5. ~~Pre-holdout audit~~ — `docs/15_preholdout_audit.md`. 7 prediction rules revised
   blind (Q2–Q4 → equivalence bounds, P3/P4/P6 → direction-only, P5 untestable);
   all committed numbers reproduce by hand; §9.9 send-route work (Apollo IS in,
   effects hold in both routes, 2/29 interactions ~ chance).
6. `output/results_2025.json` — every 2025 number extracted from artifacts for the
   results page / report brainstorm (pending with operator).

### Round 3 — DONE 2026-08-15/16. THE STUDY IS COMPLETE.

7. ~~2026 hold-out opened and scored~~ — `docs/16`. **9 held/confirmed · 4 direction ·
   4 inconclusive · 2 refuted · 1 untestable.** Confirmed: templating (−3.8pp, p=0.005)
   and why_now (+2.9pp, p=0.047) on both outcomes. Refuted and withdrawn:
   recipient_centricity (+5.3 → −0.4) and invite bullets (−9.6 → +1.3).
8. ~~Scientific + data-cleaning audit~~ — `docs/17`. No number changed. One qualifier:
   why_now's 2026 margin is fragile (2 of 5 robustness specs lift p above .05). Reply-window
   truncation resolves in the study's favour (fair 30-day window strengthens both).
9. ~~Deliverables~~ — `output/what-gets-a-reply.html` (published artifact) and
   `output/What_Gets_a_Reply_Executive.pdf` (8pp, axiomatic structure, Georgia/Helvetica,
   standardised verdict vocabulary). Both built by script from committed artefacts:
   `scripts/build_results_page.py`, `scripts/build_exec_doc.py`. 70/70 numeric audit.
10. ~~Follow-up analyses~~ — `docs/18` + `scripts/followup_analyses.py`. EXPLORATORY,
    post-holdout: structural shifts (hand-sent 73%→24%, Apollo collapsed May–Jun 2026,
    why-now 71%→54%); **NEW: same-day send volume −1.67pp per doubling, 16.4% reply at
    1–2/day vs 4.0% at 26+**, independent of templating in 2025 but dominant in 2026;
    templating-mechanism probes (4 dead ends, 1 clue: reply latency 4.8d vs 1.8d).

11. ~~Graded why-now 0–5~~ — `docs/19`, run 2026-08-17, ~$16, 177 Sonnet agents.
    Anchors + a kappa≥0.50 gate committed BEFORE grading (`041ee6c`). **Gate passed at
    0.780 — the most reliable judgment in the study**, above the binary's 0.716.
    Grade 5 = 13.5% reply vs grade 1 = 3.9% (3.5×), monotone across all six levels;
    +4.43pp 2025, +3.94pp p=0.0006 2026 (vs the binary's p=0.047 — sharper instrument,
    and without the `docs/17` §D fragility). Survives controlling `research_signal`,
    `bespokeness` and the binary. **Resolves `docs/18` §C1:** templating shallows the
    occasion (42.1% vs 62.0% specific, −0.52 grades p=0.0002) but mediates only 13% of the
    penalty. Two defects logged: §9.10 gate corpus-dependence, and the §5.3 silent drop
    for the third time (9 of 161 batches short, gap-filled).

### Next — nothing pre-registered remains

The hold-out is spent; no further 2026 test is legitimate. Open items in `docs/18` §F:
re-validate on Aug 2026+ as it accumulates, A/B test the two confirmed findings, get
Amplemarket reply attribution. The collaborative report (operator's structure, `docs/13`
§"MUST appear" pinned) is the only outstanding deliverable — and `docs/19` §4 changes what
it should say: "state a reason for writing now" is too loose to be useful coaching, because
96.4% of cold pitches already clear that bar. The defensible instruction is **the reason
has to be about the recipient, and it should drive the ask.**

## Environment

`python3` on this machine has no scipy/statsmodels, and the sandbox blocks writes to
user site-packages. Use the project venv:

```bash
.venv/bin/python        # scipy 1.13.1, statsmodels 0.14.6, pandas 2.3.3, pytest
```

`.venv/` is gitignored. Recreate with `python3 -m venv .venv && .venv/bin/pip install scipy statsmodels pandas pyarrow pytest`.

## Numbers to expect (so a wrong one is visible)

Current, after all corrections (§9.1–9.5). Any deviation means something regressed.

| | value |
|---|---|
| tests | **67 passing** |
| reply category labels | 16,695 / 16,695 — complete, validated 99.0%, do not redo |
| type labels | **38,793 across 485/485 batches** — complete |
| frame rows G30 / G21 / G45 | **12,077 / 12,558 / 11,566** |
| G30 replied / interested | **10.8% / 6.9%** |
| G30 cold_pitch replied / interested | **6.8% / 4.6%** (n=6,439) |
| §1b gate, re-measured, fresh seed | **92.8% — PASS** |
| reply-like exclusion (G30) | 3,509 |
| unlabelled candidate replies | **0** |

Superseded, in order: §1's 15.95% / 9.46% on n=14,769 → 15.3% / 9.0% on 14,174 (stale
types) → 10.9% / 6.1% on 12,077 (types complete, §9.3) → **10.8% / 6.0%** (defect 7 fixed,
§9.5). Each step is a correction, not drift; the reasoning is in the numbered sections.

## Do not

- Trust `data/missing_reply.txt` or `data/missing_type.txt`. Stale, and they hold batch
  names not ids. §9.1.
- Re-run the reply **category** pass (human vs bot vs calendar…). Already 100%, zero
  partial batches, validated at 99.0%. Note this is NOT the same as the `other_human`
  **intent** relabel, which IS happening — see the blocker above.
- Trim the type pass to frame rows only. That types 2025 corpus-wide and 2026 CA-only,
  reintroducing the asymmetry §9.2 exists to remove.
- Run any analysis before `pytest` is green and the frame invariants hold (§5.5).
- Look at 2026 results before the 2025 findings are written down and committed. The
  holdout is pre-registered in `rules/eligibility_and_analysis_rules.md` §9.

## Operator decisions, 2026-08-14

- **Relabel scope: the broken bucket only.** 4,030 `other_human` replies, 51 Fable
  batches. The other 6,927 human replies are NOT relabelled — those intents agree at
  96% and there is no reason to touch them. Saves ~$140 against relabelling all 10,957.
- **The tighter cut was offered and rejected.** Relabelling only the 1,552 frame-linked
  `other_human` replies (20 batches) would leave the reply labels half-fixed, and which
  replies "matter" shifts when the frame is rebuilt — the same class of mess as §9.2.
- **`interested` stays a real outcome.** Dropping it was offered as the largest saving
  and explicitly rejected: "dont save on replies, that matters". §1 stands — every
  finding carries both numbers.

## MUST DO before any judging spend (operator instruction, 2026-08-14)

**Prove the redaction on 20 real examples before launching a single judge agent.**

Order is fixed:
1. `python3 scripts/build_judge_batches.py`
2. `python3 scripts/check_blinding.py` — must exit 0. Non-zero blocks the launch (§5.4).
3. **Print 20 real judge items and READ them.** Confirm with your own eyes: signature gone,
   unsubscribe/legal footer gone, no sender name, no company, no dates, no URLs — AND that
   the body a judge must actually rate is still intact and not placeholder soup (§5.4
   over-redaction half; an owner surnamed *Short* once turned "a short call" into
   "a [SENDER] call").
4. Only then launch. This is not optional and is not replaceable by the checker exiting 0 —
   the checker tests for leaks, the reading tests for damage.

## Reply hygiene — verified, do not re-litigate

- Internal Encord addresses can never count as a reply: **0 of 73,856 inbound rows** come
  from `encord.com` / `encord.ai` / `tryencord.com` / `cord.tech`. The inbound set is
  defined as `is_internal_sender == False`, so a colleague replying from an Encord address
  is structurally excluded, not filtered late.
- Machine traffic is excluded by the classifier: of 16,695 candidates, **34% are machines**
  (3,188 other_bot, 1,899 calendar_bot, 564 out_of_office, 40 bounce/security/auto-ack).
  Only `category == "human"` counts as `replied`.
- Colleague-instead-of-recipient replies: measured, **13 genuine cases (0.11pp)**. The
  first estimate of 1,201 was wrong — 1,188 of those "colleagues" had been sent their own
  copy of the same invite, so their reply is already counted on their own row. Do not
  re-open this without re-checking that.

## Known limitations, measured, not blocking

| | size |
|---|---|
| non-English openers (mostly French) — English-written rubric | 61 (0.5%) |
| recipients emailed by 2+ reps — rows not fully independent | 7.2% of people, 15.6% of rows |
| genuine colleague hand-offs missed | 13 (0.11pp) |

Not yet checked: replies arriving from a personal address instead of the work one; soft
bounces arriving as ordinary mail; whether any "cold" opener actually went to an existing
customer.
