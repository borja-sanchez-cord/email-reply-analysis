# Study log — chronological record of every step and decision

(Entries appended as the study runs. Times are 2026-08-07 local unless noted.)

1. **Setup.** Git repo initialised; `.env` git-ignored; the five allowed pulling scripts
   from the old study read; nothing else in that folder opened. `CA_central/` untouched.
2. **Property discovery.** Full email/contact/company property catalogues pulled.
   129 email properties. Fill-rate probe on 3 months (1,800 emails) → `docs/01_field_choices.md`.
   Notable: `hs_object_source` separates mailbox from sequencer sends; the probe's portal
   totals already show the volume ramp (2025-03 ≈ 6.7k → 2026-05 ≈ 26.9k emails/month).
3. **Pre-registration commit `83fe035`** — eligibility rules + analysis plan committed
   before any results were computed.
4. **Owners pulled.** 236 owners; 188 with no team (70 active, 118 archived) — matches the
   brief's warning. 18 distinct team names printed and classified → `docs/02_ca_identification.md`.
   Open item: 10 "all-teams" members (CA teams + a Sales team) to be resolved from sending
   behaviour before analysis.
5. **Reply classifier protocol pre-registered** (`rules/reply_classifier_protocol.md`)
   before any reply was classified. Same for opener types (`rules/type_classifier_protocol.md`).
6. **Universe pull** Sep 2024 → Jul 2026, monthly resumable chunks, recursive splitting
   under the 10k search cap. (In progress at time of writing; counts recorded in
   `docs/03_pull_qc.md` when complete.)

## Q2 visibility note (recorded before computing anything)

Even within pushes opened from a rep mailbox, replies to *sequencer* follow-up touches may
be invisible in HubSpot (trap 1 mechanics). The follow-up curve is therefore computed two
ways — all pushes with mailbox openers, and the subset whose touches are all mailbox — and
the difference is reported rather than hidden.
