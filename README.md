# What makes a first cold email get a reply — v2 study

A from-scratch observational study of CA outbound email, run against a fresh HubSpot pull
(Sep 2024 → Jul 2026; study window Jan 2025 → Jul 2026). Two questions:

1. On the first email of a fresh push, what is linked to getting a human reply?
2. How many follow-ups were needed before a reply came?

## Ground rules

- HubSpot access is **read-only**; the token lives in `.env` (git-ignored, never printed).
- Analysis rules were **pre-registered** in `rules/` and committed before any results were
  computed — check the git log.
- The previous study's data and conclusions were not read; only its pulling machinery
  (5 named scripts) was reused, as the handoff brief allows.
- Raw data lives in `data/` (git-ignored). Every artefact in `output/` is reproducible from
  the scripts.

## Layout

- `HANDOFF_PROMPT.md` — the brief this study executes.
- `rules/` — pre-registered eligibility rules, analysis plan, judge rubric, 2026 predictions.
- `scripts/` — every pull / build / analysis step, numbered in run order.
- `docs/` — methodology decisions with the evidence behind them, written as the study ran.
- `output/` — derived tables, audit samples, and the final report.

## Deliverables

- `EXECUTIVE_SUMMARY.md` — the one-minute read: findings as tables and short sections.
- `REPORT.md` — the full plain-English write-up for sales leaders.
- `docs/` — full technical documentation: every decision, every audit, every dead end.
