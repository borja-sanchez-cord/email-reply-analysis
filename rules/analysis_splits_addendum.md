# Addendum: declared split points for numeric features

Committed before any reply-rate-by-feature number was computed. Binary features are used
as-is. Numeric features are reported two ways: (a) a headline binary split declared here,
(b) a bucket table so readers can see the shape without us choosing it post-hoc.

| feature | headline split | buckets |
|---|---|---|
| word count | ≤ 100 words vs > 100 | <50, 50–99, 100–149, 150–249, 250+ |
| sentence count | ≤ 8 vs > 8 | 1–4, 5–8, 9–12, 13+ |
| paragraph count | ≤ 4 vs > 4 | 1–2, 3–4, 5–6, 7+ |
| question count | 0 vs ≥ 1 (plus 1 vs 2+ secondary) | 0, 1, 2, 3+ |
| first question length | ≤ 12 words vs > 12 (among emails with a question) | ≤8, 9–12, 13–20, 21+ |
| links | 0 vs ≥ 1 | 0, 1, 2, 3+ |
| bullets | 0 vs ≥ 1 | 0, 1–3, 4+ |
| images | 0 vs ≥ 1 | 0, 1+ |
| subject length | ≤ 4 words vs > 4 | 1–2, 3–4, 5–7, 8+ |
| template repeats | ≥3 repeats ("templated") vs <3 | 1, 2, 3–9, 10+ |
| AI-judged 1–5 scales | top-2-box (4–5) vs rest | each point 1–5 |

Splits were chosen from convention and from the shape of cold emails generally (a hundred
words ≈ the classic "short email" threshold), not from any outcome data — none had been
computed when this was committed. If a bucket table later shows the headline split hides a
non-monotonic shape, the bucket table is reported alongside, never instead.

Per-rep consistency: primary rule as pre-registered (reps with ≥20 openers of both kinds);
a ≥10 sensitivity version is also reported when the ≥20 panel has fewer than 5 reps.
