# CA identification — evidence and decisions

Date: 2026-08-07. Source: full owner pull, active + archived (`data/owners.json`,
236 distinct owners).

## Every distinct team name (count = owners in it)

```
  8  Computer Vision UK CAs      ← CA
  6  Computer Vision US CAs      ← CA
  8  Digital Native UK CAs       ← CA
  6  Digital Native US CAs       ← CA
  6  PhysAI UK CA's              ← CA
  4  PhysAI US CA                ← CA
  7  Regulated UK CAs            ← CA
  6  Regulated US CAs            ← CA
  3  PhysAI UK                   ← ambiguous (no suffix)
  3  PhysAI US                   ← ambiguous (no suffix)
  6  Multimodal UK Sales         ← not CA
  4  Multimodal US Sales         ← not CA
  1  Solution Engineers          ← not CA
  2  Solutions                   ← not CA
  1  UK Solution Engineers       ← not CA
  6  US Solution Engineers       ← not CA
  8  Marketing Team              ← not CA
  2  Customer Success            ← not CA
```

## Decisions

1. **CA teams** = the eight teams matching `<vertical> <region> CA(s)`.
2. **`PhysAI UK` / `PhysAI US` (no suffix)**: every one of their 6 members is *also* in the
   corresponding PhysAI CA team, so these add no ambiguity — resolved as CA via their CA
   membership.
3. **All-teams members**: 10 owners (arisha, james.golby, yianni, kamil, leo, tom.inglis,
   alex.leveque, alyssa, colin, william) belong to *all four* vertical teams of their
   region, including `Multimodal <region> Sales`, which is not a CA team. That membership
   pattern looks like leads/managers added to every team rather than individual CAs.
   **Decision deferred to behavioural evidence**: their observed sending pattern
   (volume of first-touch outbound from their mailbox) decides whether they are treated as
   CAs, and the decision is documented in this file before analysis. Whatever the call,
   headline findings are re-checked with them excluded (the per-rep consistency check
   covers this).
4. **Owners with no team: 188 of 236** (70 active, 118 archived). Matches the brief's
   warning (184/235 in its earlier pull). Handling, per the pre-registered rules:
   archived-status checked first; the share of otherwise-eligible openers from
   unclassifiable senders is reported; if exclusion would discard most of the corpus, a
   documented behavioural fallback is used and reported separately from confirmed-CA
   results.
5. **Limitation (stated in the report)**: teams are today's snapshot. Anyone who changed
   role during Sep 2024 – Jul 2026 is labelled with their current team, not the team they
   had when they sent.

## Roster (confirmed CA by team membership, 32 owners)

alex.leveque*, alyssa*, andrew, arisha*, colin*, constantin, diego, gauri, george.lim,
hugo, james.golby*, james.sweeney, james.watson, joe.turner, kamil*, kat, katie,
laura.zhu, leo*, moritz, nick, nico.fernandez, ria, sachit, satchel, shivant, stewart,
tom.inglis*, william*, yianni*, yuvi (all @encord.com)

`*` = all-teams member, CA status pending behavioural evidence (decision 3).
