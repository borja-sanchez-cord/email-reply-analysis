# Counter audits — what reading 20 examples per feature actually found

The brief mandates this step because the previous study shipped findings built on a
question-counter that was counting the unsubscribe footer. Every counter here was run,
20 flagged examples printed with the underlying text, and read. Five real defects were
found and fixed; each would have produced a plausible-looking but false finding.

Audit tooling: `scripts/audit_features.py` (reproduces the exact text the counter sees,
so the audit can never disagree with the measurement). Raw audit dumps:
`output/audit_counters.txt`, `output/audit_fmt.txt`, `output/audit_q2.txt`.

## Defect 1 — tracking URLs counted as questions and as words

`https://encord.com/webinar/x/?utm_source=…` ends a "sentence" with `?`, so the question
counter scored marketing links as questions; the same URLs added 30–80 "words".

Evidence: flagged examples showed `questions found: ['com/?', 'com/lidar?', 'com/demo?']`.

Fix: collapse every URL to a single `[LINK]` token before any word/sentence/question
measurement; count links separately from the un-collapsed body.
**Effect: emails with ≥1 question fell from 27,801 (72%) to 21,411 (55%).**

## Defect 2 — unsubscribe/confidentiality footers survived the signature split

`Is this email not relevant to you?` and the legal confidentiality block were still in the
"body", adding a question and ~60 words to every email that had them.

Fix: strip the footer tail explicitly before splitting the signature, and keep the
footer-phrase blocklist on the question counter as a second line of defence.

## Defect 3 — hard-wrapped plaintext made lines look like sentences

Gmail/Outlook plaintext wraps at ~72 characters, so a single sentence spans several lines.
Splitting on newlines counted **lines as sentences** and truncated questions at the wrap
point — the audit showed questions recorded as `'coffee?'` and `'availability tomorrow or
Monday?'`. This was a systematic difference between plaintext and HTML emails, i.e. between
mail clients, not between writing styles.

Fix: `text_clean.unwrap()` joins wrapped lines within a paragraph (preserving blank lines
and bullet lines) before any measurement.
**Effect: median first-question length went from a nonsense 3 words to 10 words
(among emails with a question); mean sentences/email 8.2 → 6.0.**

## Defect 4 — signature logos and bold titles counted as body formatting

Formatting was parsed over the whole HTML, so signature logo `<img>` tags and bold job-title
lines counted as "this email uses images/bold".

Evidence: `has_bold` fired on 77% of all emails, `n_images` on 75%; inspection showed the
bold text was `'AI // ML // Computer Vision @ Encord'` — a signature line.

Fix: the HTML parser now records the **offset** of every image/bullet/bold run, and only
events falling inside the body region (before the signature cut) are counted. The
signature detector was also broadened to catch `--` delimiters, contact-block lines
(`Email:`, `Website:`, `LinkedIn:`) and org title lines (`… @ Encord`), not just sign-off
words. **Effect: has_bold 77% → 33%; mean images/email 0.9 → 0.1.**
Post-fix samples show real body emphasis: `'30% improvement in annotation accuracy'`,
`'practical 45-minute session'`, `'9th of December'`.

## Defect 5 — name and company matching fired on ordinary words

Contacts whose first name is `Or` matched the word "or"; a company called `Speak` matched
the verb "speak"; `name_beyond_greeting` fired on multi-name greetings
("Hi Ohad, David, Adi, Lee, …") because the greeting zone was only the matched prefix.

Fix: names require ≥3 characters and word boundaries; short single-word company names must
match with their capitalisation; the greeting zone is the whole first line.
**Effect: `name_beyond_greeting` 2,984 → 1,267 emails (7.7% → 2.9%).**

## Counters checked and found correct (no change)

| counter | check |
|---|---|
| `n_links` | flagged examples are real content links, signature links excluded |
| `n_bullets` | real list items; `max()` not `sum()` so HTML `<li>` isn't double-counted with its rendered `•` |
| `subject_is_question` | subject lines genuinely ending in `?` |
| `mentions_role_words` | matches "your team/work/pipeline", "as the Head of …" |
| `greeting_style` | hi 81%, hey 12%, none 3%, name_only 2%, hello 1%, dear 0.2% |
| `is_template_3plus` | flagged bodies are visibly the same email to different people |
| `not_template` (repeats == 1) | flagged bodies are visibly bespoke |
| `short` (≤60 words) | genuinely short emails, not truncations |
| `empty_body` | 0.1% (32 emails), excluded from text features |

## Standing caveat carried into the report

Template-repeat counts are sensitive to sample size (brief, trap 5): "this body appears 3+
times" is easier to hit in a larger segment. Any cross-segment comparison of templating
equalises segment sizes first.
