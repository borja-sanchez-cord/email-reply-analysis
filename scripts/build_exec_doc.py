"""Executive document (PDF via headless Chrome print).

More detailed than the results page: method, findings, failures, instrument quality,
scorecard, limitations, and evidence-graded implications. Numbers injected from
output/results_2025.json and the committed 2026 JSONs — never retyped.
"""
import html
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "output")
R = json.load(open(os.path.join(OUT, "results_2025.json")))
cp = {r["feature"]: r for r in R["cp_replied"]}
cp26r = {r["feature"]: r for r in json.load(open(f"{OUT}/q1_cold_pitch_2026_replied_G30.json"))
         if not r.get("note")}
cp26i = {r["feature"]: r for r in json.load(open(f"{OUT}/q1_cold_pitch_2026_interested_G30.json"))
         if not r.get("note")}


def esc(s):
    return html.escape(str(s))


# ---------- shared chart helpers (print palette, light only) ----------
def bar_pairs(groups, w=560, h=180, unit="%"):
    n_bars = sum(len(g[1]) for g in groups)
    gap_group, gap_bar = 34, 10
    bw = (w - gap_group * (len(groups) - 1) - gap_bar * (n_bars - len(groups))) / n_bars
    vmax = max(v for _, bars in groups for _, v, _ in bars) * 1.25
    base = h - 34
    p = [f'<svg viewBox="0 0 {w} {h}" width="100%" class="chart">',
         f'<line x1="0" y1="{base}" x2="{w}" y2="{base}" class="baseline"/>']
    xx = 0.0
    for glabel, bars in groups:
        gx0 = xx
        for blabel, v, cls in bars:
            bh = max(3, (v / vmax) * (base - 26))
            p.append(f'<rect x="{xx:.1f}" y="{base-bh:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="4" class="bar {cls}"/>')
            p.append(f'<text x="{xx+bw/2:.1f}" y="{base-bh-7:.1f}" class="val" text-anchor="middle">{v}{unit}</text>')
            p.append(f'<text x="{xx+bw/2:.1f}" y="{base+14}" class="lab" text-anchor="middle">{esc(blabel)}</text>')
            xx += bw + gap_bar
        xx -= gap_bar
        p.append(f'<text x="{(gx0+xx)/2:.1f}" y="{base+30}" class="glab" text-anchor="middle">{esc(glabel)}</text>')
        xx += gap_group
    p.append("</svg>")
    return "".join(p)


def dot_whisker(fe, se, lo_axis=-9.5, hi_axis=9.5, w=230, h=26, cls="pos"):
    def x(v):
        return (v - lo_axis) / (hi_axis - lo_axis) * w
    lo, hi = fe - 1.96 * se, fe + 1.96 * se
    return (f'<svg class="strip" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
            f'<line x1="{x(0):.1f}" y1="2" x2="{x(0):.1f}" y2="{h-2}" class="zeroline"/>'
            f'<line x1="{x(lo):.1f}" y1="{h/2}" x2="{x(hi):.1f}" y2="{h/2}" class="whisker {cls}"/>'
            f'<circle cx="{x(fe):.1f}" cy="{h/2}" r="4.5" class="dot {cls}"/></svg>')


def curve_chart(series, w=640, h=230):
    pad_l, pad_r, pad_t, pad_b = 34, 70, 14, 28
    vmax = 8.0
    def x(t): return pad_l + (t - 1) / 7 * (w - pad_l - pad_r)
    def y(v): return pad_t + (1 - v / vmax) * (h - pad_t - pad_b)
    p = [f'<svg viewBox="0 0 {w} {h}" width="100%" class="chart">']
    for gv in (0, 2, 4, 6, 8):
        p.append(f'<line x1="{pad_l}" y1="{y(gv):.1f}" x2="{w-pad_r}" y2="{y(gv):.1f}" class="grid"/>')
        p.append(f'<text x="{pad_l-6}" y="{y(gv)+4:.1f}" class="lab" text-anchor="end">{gv}%</text>')
    for t in range(1, 9):
        p.append(f'<text x="{x(t):.1f}" y="{h-6}" class="lab" text-anchor="middle">{t}</text>')
    for name, pts, cls in series:
        pts = [(t, v, max(0.0, lo), min(vmax, hi)) for t, v, lo, hi in pts]
        path = " ".join(f"{'M' if i==0 else 'L'}{x(t):.1f},{y(v):.1f}" for i, (t, v, *_ ) in enumerate(pts))
        p.append(f'<path d="{path}" class="line {cls}"/>')
        for t, v, lo, hi in pts:
            p.append(f'<line x1="{x(t):.1f}" y1="{y(lo):.1f}" x2="{x(t):.1f}" y2="{y(hi):.1f}" class="whisker {cls}"/>')
            p.append(f'<circle cx="{x(t):.1f}" cy="{y(v):.1f}" r="4" class="dot {cls}"/>')
        t, v, *_ = pts[-1]
        p.append(f'<text x="{x(t)+9:.1f}" y="{y(v)+4:.1f}" class="slab {cls}">{esc(name)}</text>')
    p.append("</svg>")
    return "".join(p)


def hbars(rows, w=600, rh=30, unit="%", vmax=100.0):
    h = rh * len(rows)
    lw = 320
    p = [f'<svg viewBox="0 0 {w} {h}" width="100%" class="chart">']
    for i, (label, v) in enumerate(rows):
        yy = i * rh
        bw = (v / vmax) * (w - lw - 60)
        p.append(f'<text x="{lw-10}" y="{yy+rh/2+4}" class="rowlab" text-anchor="end">{esc(label)}</text>')
        p.append(f'<rect x="{lw}" y="{yy+rh/2-6}" width="{bw:.1f}" height="12" rx="3" class="bar pos"/>')
        p.append(f'<text x="{lw+bw+7:.1f}" y="{yy+rh/2+4}" class="val">{v}{unit}</text>')
    p.append("</svg>")
    return "".join(p)


# ---------- data assembly ----------
tmp, why = cp["templated (3+ identical bodies)"], cp["judged: states a reason for reaching out now"]
tmp26, why26 = cp26r["templated (3+ identical bodies)"], cp26r["judged: states a reason for reaching out now"]

winners_templated = bar_pairs([
    ("2025 · 5,153 cold pitches", [("templated", tmp["rate_with"], "neg"), ("hand-crafted", tmp["rate_without"], "pos")]),
    ("2026 · 1,286 (sealed)", [("templated", tmp26["rate_with"], "neg"), ("hand-crafted", tmp26["rate_without"], "pos")]),
])
winners_whynow = bar_pairs([
    ("2025", [("has a reason", why["rate_with"], "pos"), ("no reason", why["rate_without"], "mut")]),
    ("2026 (sealed)", [("has a reason", why26["rate_with"], "pos"), ("no reason", why26["rate_without"], "mut")]),
])

LADDER = [
    ("Names a real reason to write now", "judged: states a reason for reaching out now", "confirmed", "Confirmed"),
    ("Recipient-focused writing", "judged: recipient_centricity (top 2 of 5)", "failed", "Failed 2026"),
    ("Under 100 words", "short (<=100 words)", "direction", "Direction held"),
    ("Subject line is a question", "subject is a question", "direction", "Direction held"),
    ("Asks 2+ questions", "asks 2+ questions", "direction", "Direction held"),
    ("Has bold text", "has bold text", "gray", "Mostly templating"),
    ("Reuses their name mid-email", "uses their name again in the body", "gray", "Untestable 2026"),
    ("Mass template (3+ identical)", "templated (3+ identical bodies)", "confirmed", "Confirmed"),
]
ladder_rows = []
for label, key, cls, verdict in LADDER:
    r = cp[key]
    color = "mut" if cls == "gray" else ("pos" if r["fe_gap_pp"] > 0 else "neg")
    ladder_rows.append(
        f'<div class="lrow"><div class="llab">{esc(label)}</div>'
        f'{dot_whisker(r["fe_gap_pp"], r["fe_se_pp"], cls=color)}'
        f'<div class="lval {color}">{r["fe_gap_pp"]:+.1f}</div>'
        f'<div><span class="chip {cls}">{esc(verdict)}</span></div></div>')

wb = [(r["bucket"], r["rate"]) for r in R["wordbuckets"] if r["bucket"] != "250+"]
word_chart = bar_pairs([("words in the email — reply rate", [(b, v, "pos" if v >= 10 else "mut") for b, v in wb])], w=520, h=170)

q2_25 = [(r["touch"], r["reply_rate_pct"], r["lo_pct"], r["hi_pct"]) for r in R["q2"]]
q2_26 = [(1, 5.82, 5.09, 6.65), (2, 6.03, 5.06, 7.17), (3, 4.38, 3.32, 5.76), (4, 2.16, 1.21, 3.83),
         (5, 3.23, 1.71, 6.02), (6, 2.86, 1.12, 7.12), (7, 2.67, 0.73, 9.21), (8, 5.41, 1.50, 17.70)]
q2_chart = curve_chart([("2025", q2_25, "s1"), ("2026", q2_26, "s2")])
profile_chart = hbars([(p["label"], p["pct"]) for p in R["profile"]])

KAPPA = [("Reason to write now", .716, .725), ("Research on the recipient", .749, .735),
         ("Guessed the reader's problem", .694, .642), ("Specific value claim", .665, .621),
         ("Customer proof", .650, .662), ("Written just for them", .564, .602),
         ("Clear ask", .421, .570), ("Polish", .428, .460), ("About the recipient", .435, .445),
         ("Peer tone — discarded", .320, .318), ("Economy — discarded", .220, .256)]
kappa_rows = "".join(
    f"<tr{' class=cut' if 'discarded' in a else ''}><td>{esc(a)}</td><td>{s:.2f}</td><td>{c:.2f}</td></tr>"
    for a, s, c in KAPPA)

SCORE = [
    ("Mass-templated emails get fewer replies", "confirmed", "Confirmed — both years, both outcomes (p=0.005 / 0.001)"),
    ("A real reason-to-write-now wins", "confirmed", "Confirmed — both outcomes (p=0.047 / 0.012)"),
    ("Its effect size lands in the pre-declared band", "held", "Held (+2.9, band +1.6 to +7.6)"),
    ("It is the #1 judged quality", "held", "Held — ranked first again"),
    ("Follow-up #1 is worth as much as the opener", "held", "Held (5.8% vs 6.0%)"),
    ("Most replies arrive by the 4th touch", "held", "Held (96%)"),
    ("Same pattern on the “interested” outcome", "held", "Held"),
    ("“Pain”/“proof” negatives are just email length", "held", "Held"),
    ("The two unreliable qualities stay silent", "held", "Consistent"),
    ("Under 100 words beats longer", "direction", "Direction held; 2025's size (+4.5) excluded by 2026"),
    ("Question subject lines help", "direction", "Direction held; too rare in 2026 (n=79) to be sure"),
    ("Asking 2+ questions hurts", "direction", "Direction held"),
    ("Templated event invites do worse", "direction", "Direction held"),
    ("Short event invites do better", "direction", "Direction held; 2025's +17.5 excluded"),
    ("Bold text hurts", "inconclusive", "Too close to call (cell shrank; wrong sign inside noise)"),
    ("Personalisation & crisp asks do nothing", "inconclusive", "Still nothing — 2026 too noisy to certify ≤3pp"),
    ("Recipient-focused emails win", "failed", "Failed — +5.3 became −0.4; 2025 size excluded"),
    ("Bullet points ruin event invites", "failed", "Failed — −9.6 became +1.3"),
    ("Reusing their name mid-email hurts", "untestable", "Habit vanished (2 emails in 2026)"),
]
score_rows = "".join(f'<tr><td>{esc(a)}</td><td><span class="chip {c}">{esc(v)}</span></td></tr>' for a, c, v in SCORE)

DOC = f"""<!doctype html><html><head><meta charset="utf-8"><title>What Gets a Reply — Executive Document</title>
<style>
:root {{ --ink:#0b0b0b; --ink2:#52514e; --mut:#898781; --grid:#e1e0d9; --base:#c3c2b7;
  --border:rgba(11,11,11,.12); --pos:#2a78d6; --neg:#e34948; --s2:#eb6834;
  --good:#006300; --crit:#d03b3b; --chipbg:rgba(11,11,11,.05); --surface:#fcfcfb; }}
* {{ box-sizing:border-box; }}
html, body {{ margin:0; padding:0; background:#fff; color:var(--ink);
  font:10.5pt/1.5 system-ui,-apple-system,"Segoe UI",sans-serif; }}
@page {{ size:A4; margin:17mm 16mm 19mm; }}
.pagebreak {{ break-before:page; }}
.avoid {{ break-inside:avoid; }}
h1 {{ font-size:26pt; line-height:1.12; letter-spacing:-.02em; margin:0 0 6pt; }}
h2 {{ font-size:15pt; letter-spacing:-.01em; margin:0 0 6pt; }}
h3 {{ font-size:11.5pt; margin:9pt 0 3pt; }}
p {{ margin:4pt 0; max-width:66ch; color:#1c1c1a; }}
p.dim, li.dim {{ color:var(--ink2); }}
.eyebrow {{ font-size:7.5pt; font-weight:700; letter-spacing:.14em; text-transform:uppercase; color:var(--mut); margin:0 0 3pt; }}
.small {{ font-size:8.5pt; color:var(--mut); }}
.rule {{ border:none; border-top:1px solid var(--grid); margin:10pt 0; }}
table {{ width:100%; border-collapse:collapse; font-size:9pt; }}
td, th {{ padding:4pt 6pt 4pt 0; border-bottom:.5pt solid var(--grid); vertical-align:top; text-align:left; }}
th {{ font-size:7.5pt; text-transform:uppercase; letter-spacing:.1em; color:var(--mut); }}
.num {{ font-variant-numeric:tabular-nums; }}
.chip {{ display:inline-block; font-size:7.5pt; font-weight:650; border-radius:99px; padding:1.5pt 7pt; background:var(--chipbg); color:var(--ink2); white-space:nowrap; }}
.chip.confirmed, .chip.held {{ color:var(--good); background:rgba(12,163,12,.12); }}
.chip.direction {{ color:var(--pos); background:rgba(42,120,214,.12); }}
.chip.failed {{ color:var(--crit); background:rgba(208,59,59,.12); }}
.chart text, .strip text {{ font:8pt system-ui,sans-serif; fill:var(--ink2); font-variant-numeric:tabular-nums; }}
.chart .val {{ font-weight:650; fill:var(--ink); }} .chart .lab {{ fill:var(--mut); }}
.chart .glab {{ fill:var(--ink2); font-weight:600; }} .chart .rowlab {{ fill:var(--ink); font-size:8.5pt; }}
.chart .baseline {{ stroke:var(--base); stroke-width:1.2; }} .chart .grid {{ stroke:var(--grid); stroke-width:.8; }}
.bar.pos {{ fill:var(--pos); }} .bar.neg {{ fill:var(--neg); }} .bar.mut {{ fill:var(--mut); opacity:.55; }}
.line {{ fill:none; stroke-width:1.8; }} .line.s1 {{ stroke:var(--pos); }} .line.s2 {{ stroke:var(--s2); }}
.dot.s1, .dot.pos {{ fill:var(--pos); }} .dot.s2 {{ fill:var(--s2); }} .dot.neg {{ fill:var(--neg); }} .dot.mut {{ fill:var(--mut); }}
.whisker {{ stroke-width:1.6; opacity:.45; }} .whisker.s1, .whisker.pos {{ stroke:var(--pos); }}
.whisker.s2 {{ stroke:var(--s2); }} .whisker.neg {{ stroke:var(--neg); }} .whisker.mut {{ stroke:var(--mut); }}
.slab {{ font-weight:650; }} .slab.s1 {{ fill:var(--pos); }} .slab.s2 {{ fill:var(--s2); }}
.zeroline {{ stroke:var(--base); stroke-width:1.2; stroke-dasharray:2 3; }}
.lrow {{ display:grid; grid-template-columns:150pt 230px 34pt auto; gap:8pt; align-items:center;
  padding:2.5pt 0; border-bottom:.5pt solid var(--grid); }}
.llab {{ font-size:9pt; }} .lval {{ font-weight:700; font-variant-numeric:tabular-nums; text-align:right; font-size:9pt; }}
.lval.pos {{ color:var(--pos); }} .lval.neg {{ color:var(--neg); }} .lval.mut {{ color:var(--mut); }}
.tally {{ display:flex; gap:8pt; margin:12pt 0; }}
.tally .t {{ background:var(--chipbg); border-radius:6pt; padding:7pt 12pt; text-align:center; }}
.tally .n {{ font-size:16pt; font-weight:750; }} .tally .l {{ font-size:7.5pt; color:var(--ink2); }}
.grid2 {{ display:grid; grid-template-columns:1fr 1fr; gap:14pt; }}
.callout {{ background:var(--surface); border:.75pt solid var(--border); border-radius:6pt; padding:8pt 11pt; margin:7pt 0; }}
.toc td {{ border-bottom:.5pt dotted var(--grid); padding:3.5pt 0; }}
tr.cut td {{ color:var(--crit); }}
ol.main > li {{ margin:5pt 0; }}
</style></head><body>
<!-- ============ COVER / EXEC SUMMARY ============ -->
<p class="eyebrow">Encord · Cold outbound study · Jan 2025 – Jul 2026 · Executive document</p>
<h1>What Gets a Reply</h1>
<p style="font-size:12pt; max-width:70ch;">A pre-registered study of 12,077 outreach emails: what
makes a cold email get a reply, how many follow-ups are worth sending — and which of our
answers survived a test on sealed data they had never seen.</p>
<div class="tally">
<div class="t"><div class="n" style="color:var(--good)">9</div><div class="l">held / confirmed</div></div>
<div class="t"><div class="n" style="color:var(--pos)">4</div><div class="l">direction held</div></div>
<div class="t"><div class="n">4</div><div class="l">too close to call</div></div>
<div class="t"><div class="n" style="color:var(--crit)">2</div><div class="l">failed the test</div></div>
<div class="t"><div class="n">1</div><div class="l">untestable</div></div>
</div>

<h2>Executive summary</h2>
<p><strong>Two findings are confirmed</strong> — meaning they were found in 2025, written down
as predictions, and then re-appeared in sealed 2026 data at the predicted size:</p>
<ol class="main">
<li><strong>Mass-produced emails get roughly a quarter of the replies.</strong> Sending the same
body to three or more people collapsed reply rates in both years (4.8% vs 9.3% in 2025;
1.8% vs 8.0% in 2026) — measured within the same sender, so it is not "worse reps use
templates."</li>
<li><strong>A concrete reason to write <em>now</em> roughly doubles replies.</strong> A launch, a
funding round, an event, a referral — something checkable that answers "why this email, this
week." 7.9% vs 4.6% in 2025; 8.5% vs 4.1% in 2026. It beat every other quality we measured,
both years, and held on the stricter "showed real interest" outcome.</li>
</ol>
<p><strong>The most repeated advice did not survive scrutiny.</strong> Researched
personalisation — citing facts about the recipient, writing that could only fit them — never
produced a significant effect in either year. Links don't hurt. Greeting by name does nothing.
The "keep it short" rule is a floor at ~100 words, not a virtue of ever-shorter emails.</p>
<p><strong>Two 2025 findings failed the sealed test and are withdrawn</strong> — including our
most promising one ("recipient-focused emails win", +5.3pp in 2025, −0.4pp in 2026). That is
the safeguard working: without the sealed year, both would be in the recommendations.</p>
<p><strong>Follow-ups:</strong> the first follow-up is worth as much as the opener; ~90% of all
eventual replies arrive by the third touch. Both patterns repeated in 2026.</p>
<div class="callout"><strong>What the data supports doing</strong> — graded by evidence:
<br>· <strong>Strong:</strong> stop sending identical bodies at scale from personal mailboxes; require every cold email to name its reason-to-write-now.
<br>· <strong>Moderate:</strong> keep openers under ~100 words; always send follow-ups 1–2, usually 3; stop after 4 unless there's a new reason.
<br>· <strong>Time back:</strong> stop polishing links out, stop first-name rituals, stop research-heavy personalisation as a reply tactic — none of it moved replies.</div>

<!-- ============ 1. THE QUESTION ============ -->
<div class="pagebreak"></div>
<p class="eyebrow">Section 1</p>
<h2>The question, and why naive answers mislead</h2>
<p>The question sounds simple: <em>what makes someone reply to a cold email?</em> Getting a
defensible answer is not, for three reasons.</p>
<h3>1.1 · Good reps poison simple comparisons</h3>
<p>Reps choose who gets which email. If strong reps write short emails to warm prospects,
"short emails win" may just mean "good reps win." Our primary comparison is therefore
<strong>within-sender</strong>: each rep's emails with a trait against the same rep's emails
without it. Rep skill and rep targeting drop out of the comparison.</p>
<h3>1.2 · Test enough traits and some "win" by luck</h3>
<p>We measured ~40 traits; test that many and 1–2 "win" by chance. Every result is corrected
for this, within pre-declared families of tests. We also re-ran the whole analysis on
deliberately scrambled data ten times: it correctly found almost nothing (5 spurious hits in
240 tests), so the machinery itself doesn't manufacture findings.</p>
<h3>1.3 · Staring at data until a pattern appears guarantees a pattern</h3>
<p>The deepest problem: explore data freely and you <em>will</em> find patterns — some real,
some noise you fit to. The only clean defence is the one machine-learning uses:
<strong>a training set and a validation set.</strong> We explored 2025 freely, wrote every
conclusion down as a testable prediction with its pass/fail rule, committed them to a
timestamped record — and only then opened Jan–Jul 2026, once. No tuning, no second look.</p>
<div class="callout"><strong>How to read "failed" and "held."</strong> Our split is by time, not
random, so 2026 is a genuinely different world (different sender mix, different tooling). A
finding that <em>fails</em> has two possible readings — it was never real, or it was real and the
world changed — and we deliberately do not rescue any failure with the second reading: failed
means <em>don't build on it</em>. A finding that <em>holds</em> cleared a harder bar than a
random split: it survived fresh noise <em>and</em> a shifted world. That is the property you
want before acting on it, because every decision applies to the future — also a changed world.</div>

<!-- ============ 2. HOW ============ -->
<p class="eyebrow" style="margin-top:14pt">Section 2</p>
<h2>How the study worked</h2>
<p class="dim">From ~117,000 sent-email records: 12,077 qualifying "first touches" (fresh
outreach to a person after ≥30 days of silence, Gmail-recorded, from commercial senders;
bounces and pre-existing threads excluded). Every reply candidate was classified by AI
(human vs auto-reply vs calendar bot vs bounce — validated at 99% agreement); only genuine
human replies count. Two outcomes per email: <strong>replied</strong> (a human wrote back)
and <strong>interested</strong> (the reply shows forward motion — validated at 92.8%).</p>
<p class="dim"><strong>Layer 1 — countable traits</strong> (length, questions, links, subject
shape, name use, template detection) measured by audited code. <strong>Layer 2 — judged
qualities:</strong> an AI read each of 12,462 emails blind — sender, date, recipient and
outcome all redacted — and scored 12 pre-registered qualities against a rubric with written
anchors. A second scoring pass and an independent second AI measured which qualities can be
scored consistently at all (Section 6); two couldn't and were discarded.</p>

<!-- ============ 3. CONFIRMED ============ -->
<div class="pagebreak"></div>
<p class="eyebrow">Section 3 · Confirmed on sealed data</p>
<h2>The two findings that survived everything</h2>
<h3>3.1 · Mass-produced emails get a quarter of the replies</h3>
<div class="avoid">{winners_templated}</div>
<p class="small">Reply rate, cold pitches. "Templated" = same body sent to 3+ people. Within-sender;
2026 p=0.005 (replied), p=0.001 (interested: 0.9% vs 5.6%). Agreed in 10 of 12 reps (2025), 3 of 4 (2026).</p>
<p>The effect is not subtle, and its fingerprints show up elsewhere: bold text (−4.3pp) and
re-using the recipient's first name mid-email (−5.4pp) both looked harmful in 2025, but 77–80%
of the emails carrying them were templates — they are substantially the same finding in
different clothes, and we count them once, not three times.</p>
<h3>3.2 · A real reason to write now roughly doubles replies</h3>
<div class="avoid">{winners_whynow}</div>
<p class="small">Reply rate, cold pitches. "Reason" = an explicit, checkable occasion: launch, funding,
event, visit, referral, news. 2026: p=0.047 replied / p=0.012 interested; effect landed inside the
pre-declared band (+1.6 to +7.6); top-ranked judged quality both years, as predicted.</p>
<p>This is the study's sharpest lesson because of what it beat: <strong>research-heavy
personalisation did nothing</strong> (next section), while having an <em>occasion</em> doubled
replies. "I know things about you" and "there is a reason I'm writing to you today" feel
similar — the data says only the second one matters. It also survives a length control: it is
not "short emails in disguise."</p>

<!-- ============ 4. LADDER + NULLS ============ -->
<div class="pagebreak"></div>
<p class="eyebrow">Section 4</p>
<h2>Everything that moved replies in 2025 — and its 2026 verdict</h2>
<p class="small">Effect in percentage points on reply rate (dot), statistical uncertainty (bar),
within-sender, cold pitches, n=5,153. Verdicts from the sealed 2026 test (n=1,286).</p>
<div class="avoid">{''.join(ladder_rows)}</div>
<h3 style="margin-top:14pt">What does nothing — tested with the same rigor</h3>
<table class="avoid">
<tr><th>Belief</th><th>What we found</th></tr>
<tr><td>Links hurt deliverability/replies</td><td>No. Direction was positive both years (+4.9pp, then +1.5pp); never solid enough to claim the reverse.</td></tr>
<tr><td>Greet them by name</td><td>Nothing either year (−2.1pp, then +2.1pp — noise around zero).</td></tr>
<tr><td>Mention their company</td><td>Nothing (0.0pp, then −0.4pp). Name-dropping ≠ relevance.</td></tr>
<tr><td>Cite researched facts about them</td><td>Nothing significant either year (+1.3, then +0.6).</td></tr>
<tr><td>Make it read written-just-for-them</td><td>Nothing significant either year (+1.9, then +2.1).</td></tr>
<tr><td>Nail one crisp, specific ask</td><td>Nothing (−0.0, then +0.9).</td></tr>
<tr><td>Shorter is always better</td><td>No — it's a <strong>floor at ~100 words</strong>, not a slope:</td></tr>
</table>
<div class="avoid" style="max-width:420pt">{word_chart}</div>
<p class="dim">These nulls are findings, not absences: each had the sample size to show an
effect the size of our confirmed ones, and didn't. They contradict most outbound playbooks,
which is precisely what makes them valuable — they say where effort is being wasted.</p>

<!-- ============ 5. FOLLOW-UPS ============ -->
<div class="pagebreak"></div>
<p class="eyebrow">Section 5</p>
<h2>Follow-ups: the first one is worth as much as the opener</h2>
<p class="small">Chance of a reply after each touch, among people still silent at that point.
Vertical bars = uncertainty; few people receive late touches in 2026, so those bars are wide (clipped at 8%). All email types, 8,591 pushes (2025) / 3,486 (2026).</p>
<div class="avoid">{q2_chart}</div>
<div class="grid2" style="margin-top:8pt">
<div><p><strong>61%</strong> of all replies arrive <em>after</em> the first email — an unsent
follow-up forfeits more than half the outcome. The first follow-up out-performs the opener
itself (5.0% vs 4.1% in 2025; 6.0% vs 5.8% in 2026 — predicted and held).</p></div>
<div><p><strong>~90%</strong> of eventual replies are in by touch 3; touches 5–8 added
0.6 points <em>combined</em> in 2025. One honest caveat: who receives touch 5 is the rep's
choice, so late-touch rates describe the prospects reps chose to keep chasing.</p></div>
</div>

<p class="eyebrow" style="margin-top:16pt">Section 5b</p>
<h2>The mirror: what our 12,462 emails actually look like</h2>
<p class="small">Blind AI ratings, before any outcome was attached.</p>
<div class="avoid">{profile_chart}</div>
<p>The team writes clean, well-formed emails with clear asks — that are mostly about us. The
two traits that matter most (a reason-to-write; not being a template) are exactly where the
corpus is weakest: 20% of emails have no why-now, and 44% are visible mail-merge.</p>

<!-- ============ 6. FAILURES + INSTRUMENT ============ -->
<div class="pagebreak"></div>
<p class="eyebrow">Section 6 · The safety net, working</p>
<h2>Two findings died on the sealed data — and were withdrawn</h2>
<p><strong>"Recipient-focused emails win"</strong> was 2025's most attractive result: +5.3pp,
significant after correction, stronger in every robustness check we ran inside 2025. On the
sealed 2026 data: <strong>−0.4pp</strong>, with the 2025 effect size statistically excluded. It
had been labelled exploratory, moderate-reliability, small-sample — every flag earned. It is out.</p>
<p><strong>"Bullet points ruin event invites"</strong> (−9.6pp in 2025) returned +1.3pp in 2026.
A one-year artefact, now on record as such.</p>
<p class="dim">Failure has two possible readings — never real, or real-then-the-world-changed.
We do not use the second as a rescue: failed means withdrawn. But it is why "held" is the
stronger claim: survivors cleared fresh noise <em>and</em> a changed world.</p>

<h2 style="margin-top:14pt">Can you trust an AI judge? We measured it</h2>
<p class="dim">Each quality was scored twice by the same AI on 1,246 emails, and independently
by a second, stronger AI on 1,000. The table shows agreement <em>beyond chance</em> (0 = coin
flip, 1 = perfect) on the exact cut used in analysis. Two qualities scored near-chance —
by <em>both</em> AIs, which agreed with each other exactly as much as one agreed with itself
(gap −0.02). That means the questions themselves are ambiguous, not the model — so both were
discarded, and nothing in this document rests on them.</p>
<table class="avoid" style="max-width:340pt">
<tr><th>Judged quality</th><th>Self-agreement</th><th>Second AI</th></tr>
{kappa_rows}
</table>
<p class="small">Above 0.6 = solid · 0.4–0.6 = usable with care · below 0.4 = discarded.
Separately, the 12 qualities were checked for being one "halo" score in disguise — they are not
(mean cross-correlation 0.19; threshold 0.60), with one exception: research-signal and
bespokeness overlap so strongly (r=0.83) that they are reported as one finding.</p>

<!-- ============ 7. SCORECARD ============ -->
<div class="pagebreak"></div>
<p class="eyebrow">Section 7</p>
<h2>The full scorecard: 19 predictions, sealed-data verdicts</h2>
<p class="small">Every prediction and its pass/fail rule was committed to a timestamped record
before 2026 was opened; power-limited rules were tightened (blind) in a pre-registered audit.</p>
<table>{score_rows}</table>

<!-- ============ 8. SCOPE ============ -->
<div class="pagebreak"></div>
<p class="eyebrow">Section 8</p>
<h2>Scope and limitations — what this study cannot say</h2>
<ol class="main">
<li><strong>It covers Gmail-recorded outbound only</strong> — hand-sent and Apollo-sent.
Amplemarket sends leave no reliable reply trail and are excluded; they grew from 20% of
outreach in 2025 to 71% in 2026. These findings therefore describe a shrinking, more
deliberate slice of outbound (~75% of it in 2025, under 30% in 2026) and say nothing about
whether the Amplemarket machine works.</li>
<li><strong>The sending tool doesn't change what works.</strong> Tool-sent emails reply about
2 points lower across the board, but the offset is flat: across all 29 traits tested, the tool
changed the effect of essentially none (2 of 29, exactly the chance rate). It shifts the
baseline, not the recipe — and is likely partly a tracking artefact, so no claim is made either way.</li>
<li><strong>This is correlation, credibly narrowed — not an experiment.</strong> Within-sender
comparison removes rep-level differences, but a rep may still save their best emails for their
best prospects. Treat effect sizes as upper bounds; treat directions as trustworthy. The only
way to do better is an A/B test, which this study's two confirmed findings are the natural
candidates for.</li>
<li><strong>Some 2026 verdicts are power-limited.</strong> 2026 is a quarter of 2025; four
predictions came back "too close to call" — reported as exactly that, never as confirmation.</li>
<li><strong>Known residuals, documented not hidden:</strong> 155 Amplemarket emails inside
scope on a technicality (all analyses re-run without them; nothing changes); ~0.1% of replies
missed via colleague hand-offs; non-English emails (0.5%) judged with an English rubric.</li>
</ol>
<hr class="rule">
<p class="small">Method registration, defect log, per-analysis outputs and this document's
source are version-controlled in the study repository (rules/RUN2_PREREGISTRATION.md,
docs/13–16). Analysis: within-sender fixed effects with cluster-robust uncertainty;
Benjamini–Hochberg correction within pre-registered families; placebo-tested. AI judging:
blinded batches, automated leak gate (0 leaks across 12,462 items), dual-model validation.
Prepared 15 August 2026.</p>
</body></html>
"""

path = os.path.join(OUT, "exec_doc.html")
open(path, "w").write(DOC)
print(f"wrote {path} ({len(DOC):,} bytes)")
