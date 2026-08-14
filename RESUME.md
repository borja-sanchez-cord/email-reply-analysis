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

Stage 0 (tests) done and committed. Stage 1 (type labels) part-done and safe to resume.
**The §1b gate on `interested` FAILED at 83.3% — see `docs/11_intent_accuracy_gate.md`.
That blocks Layer-2 use of `interested` and is the first thing to deal with.**
No analysis has been run. No email has been judged. Zero results exist.

## BLOCKER: the intent gate failed — read docs/11 before anything else

The whole 17-point gap is one bucket. All eight real intents agree at 96.2%; the
`other_human` catch-all (39% of the sample) agrees at 62.9%. Fix that bucket and the
gate reads 97.7%.

The sequence in `docs/11_intent_accuracy_gate.md` is: **adjudicate the 116 disputed
`other_human` replies first**, under a sharpened written definition, THEN re-label
(~137 Fable batches), THEN re-measure on a **fresh seed**. Do not re-measure on seed
20260814 — that measures the tuning, not the classifier.

Two things that must not happen: tuning pass A until it agrees with pass B (pass B has
its own errors — it called a decline containing a question mark `asks_for_information`),
and redefining `interested` to make the gate pass.

## Exactly where to pick up

### Step 1 — see what actually landed

```bash
cd /Users/borja/builds/v2_email_replies_analysis
ls output/type_labels | wc -l          # target 485
ls output/intent_accuracy/second_pass_*.json 2>/dev/null | wc -l   # target 6
```

Then list the still-missing type batches (this is the authoritative check — the
`data/missing_*.txt` files are stale snapshots and hold batch names, not ids):

```bash
.venv/bin/python - <<'PY'
import glob, os
miss=[os.path.basename(p)[:-5] for p in sorted(glob.glob("output/type_batches/batch_*.json"))
      if not os.path.exists("output/type_labels/"+os.path.basename(p))]
print(len(miss)); print(miss)
PY
```

### Step 2 — re-launch only what is missing

Both workflows are **idempotent**: each agent skips a batch whose output already
exists, so re-running with the full list is safe. Pass the missing list as `args`.

- Type labels: `Workflow({scriptPath: ".../type-label-gap-wf_93e9a651-ac7.js", args: [<missing batch names>]})`
- Intent pass B: `Workflow({scriptPath: ".../intent-accuracy-pass-b-wf_77b3cadf-860.js", args: ["pack_0",...,"pack_5"]})`

Scripts live in
`/Users/borja/.claude/projects/-Users-borja-builds-v2-email-replies-analysis/561529db-b3dc-45de-992e-44d0f2e3e129/workflows/scripts/`.
Both use **Fable** — matching the instrument that produced the other 24,960 labels
(§8.3). Do not switch models mid-classification; the split would fall on 2025-vs-2026,
which is the exact defect §9.2 exists to fix.

### Step 3 — then, in this order (no stage starts before the previous asserts pass)

```bash
.venv/bin/python -m pytest tests/ -q                 # must be 30 passed
.venv/bin/python scripts/assemble_labels.py          # expect 485/485 clean, 38,793 type labels
.venv/bin/python scripts/build_frame.py 30           # then 21, then 45
.venv/bin/python scripts/intent_accuracy.py          # the §1b GATE — must be >=90%
```

The §1b gate is a **hard gate**: if Interested-level agreement is below 90%, the intent
classifier is revised and re-measured before any Layer-2 analysis uses `interested`.

After that: Layer-1 analysis → placebo test → judge batches → `check_blinding.py`
(must exit 0 or the judges do not launch) → judging. Full order in §6.

## Environment

`python3` on this machine has no scipy/statsmodels, and the sandbox blocks writes to
user site-packages. Use the project venv:

```bash
.venv/bin/python        # scipy 1.13.1, statsmodels 0.14.6, pandas 2.3.3, pytest
```

`.venv/` is gitignored. Recreate with `python3 -m venv .venv && .venv/bin/pip install scipy statsmodels pandas pyarrow pytest`.

## Numbers to expect (so a wrong one is visible)

| | value |
|---|---|
| reply labels | 16,695 / 16,695 — complete, do not redo |
| type labels when done | 38,793 across 485 batches |
| frame G30 rows, stale type labels | 15,586 |
| frame G30 rows, after re-assembly | 14,174 (reply-like exclusion rose 817 → 1,412) |
| frame G30 rows, final | **not yet known** — will fall again once the 2026 window is typed |
| replied / interested at G30 | 15.3% / 9.0% before the 2026 window lands |

The §1 baselines (15.95% / 9.46% on n=14,769) are superseded — see §9.3.

## Do not

- Trust `data/missing_reply.txt` or `data/missing_type.txt`. Stale, and they hold batch
  names not ids. §9.1.
- Re-label replies. Already 100%, zero partial batches.
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
