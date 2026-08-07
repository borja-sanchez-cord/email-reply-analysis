# Fresh-push gap G — evidence and choice

151,332 inter-touch gaps across 72,889 recipients (all outbound channels).
Full distribution: `output/gap_distribution.csv`.

Shape:
- **0–14 days: the bump/sequence cluster.** 80% of all gaps. Day 14 still has 1,914; day
  15 halves to 1,057, decaying to ~700 by day 21.
- **Days 27–29: a distinct secondary bump** (479/611 vs ~330 around it) — monthly-cadence
  follow-ups. These are scheduled steps of the same outreach, not new pushes.
- **Days 30–32: the local minimum after the cluster** (295/181/216), settling into a flat
  tail (~100–250/day) with no further structure.

There is **no single sharp trough**; the honest description is "cluster ends ~day 15,
monthly-cadence bump at ~28, background tail from ~day 30". The cut is placed **after**
the monthly bump, at its local minimum:

**G = 30 days.** A first email after ≥30 days of silence starts a new push.

Pre-registered robustness: the entire pipeline re-runs at **G = 21** (treats monthly-
cadence steps as new pushes — aggressive) and **G = 45** (conservative). Headline findings
that flip across 21/30/45 are reported as unstable.

Note: the handoff brief's earlier corpus estimate also used a 30-day gap, so its
sanity-check counts (~4,300 confirmed-CA 2025 openers) are directly comparable — this was
noticed after choosing the cut from our own distribution, and did not drive the choice
(the 27–29-day bump did).
