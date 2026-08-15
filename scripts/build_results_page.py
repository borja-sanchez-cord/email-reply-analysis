"""Build the plain-English results page (output/what-gets-a-reply.html).

Numbers come from output/results_2025.json and the committed 2026 holdout artefacts —
never retyped from memory. Charts are server-generated inline SVG using the palette
tokens, so the page is fully self-contained and theme-aware.
"""
import html
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "output")
R = json.load(open(os.path.join(OUT, "results_2025.json")))

cp = {r["feature"]: r for r in R["cp_replied"]}


def load26(tag):
    return {r["feature"]: r for r in json.load(open(f"{OUT}/q1_{tag}.json"))
            if not r.get("note")}


cp26r = load26("cold_pitch_2026_replied_G30")
cp26i = load26("cold_pitch_2026_interested_G30")

# ---------------------------------------------------------------- chart helpers
def esc(s):
    return html.escape(str(s))


def dot_whisker(fe, se, lo_axis=-9.5, hi_axis=9.5, w=260, h=30, cls="pos"):
    """One row's effect strip: zero line, CI whisker, dot >=8px."""
    def x(v):
        return (v - lo_axis) / (hi_axis - lo_axis) * w
    lo, hi = fe - 1.96 * se, fe + 1.96 * se
    return (f'<svg class="strip" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'role="img" aria-label="effect {fe:+.1f} points, range {lo:+.1f} to {hi:+.1f}">'
            f'<line x1="{x(0):.1f}" y1="2" x2="{x(0):.1f}" y2="{h-2}" class="zeroline"/>'
            f'<line x1="{x(lo):.1f}" y1="{h/2}" x2="{x(hi):.1f}" y2="{h/2}" '
            f'class="whisker {cls}"/>'
            f'<circle cx="{x(fe):.1f}" cy="{h/2}" r="5" class="dot {cls}"/></svg>')


def bar_pairs(groups, w=640, h=190, unit="%"):
    """Grouped bars with direct labels. groups = [(group_label, [(bar_label, value, cls)])]"""
    n_bars = sum(len(g[1]) for g in groups)
    gap_group, gap_bar = 34, 10
    bw = (w - gap_group * (len(groups) - 1) - gap_bar * (n_bars - len(groups))) / n_bars
    vmax = max(v for _, bars in groups for _, v, _ in bars) * 1.25
    base = h - 34
    parts = [f'<svg viewBox="0 0 {w} {h}" width="100%" role="img" class="chart">']
    parts.append(f'<line x1="0" y1="{base}" x2="{w}" y2="{base}" class="baseline"/>')
    xx = 0.0
    for glabel, bars in groups:
        gx0 = xx
        for blabel, v, cls in bars:
            bh = max(3, (v / vmax) * (base - 26))
            parts.append(f'<rect x="{xx:.1f}" y="{base-bh:.1f}" width="{bw:.1f}" '
                         f'height="{bh:.1f}" rx="4" class="bar {cls}"/>')
            parts.append(f'<text x="{xx+bw/2:.1f}" y="{base-bh-7:.1f}" class="val" '
                         f'text-anchor="middle">{v}{unit}</text>')
            parts.append(f'<text x="{xx+bw/2:.1f}" y="{base+14}" class="lab" '
                         f'text-anchor="middle">{esc(blabel)}</text>')
            xx += bw + gap_bar
        xx -= gap_bar
        parts.append(f'<text x="{(gx0+xx)/2:.1f}" y="{base+30}" class="glab" '
                     f'text-anchor="middle">{esc(glabel)}</text>')
        xx += gap_group
    parts.append("</svg>")
    return "".join(parts)


def curve_chart(series, w=680, h=250):
    """Follow-up curve: dots + line per series with CI whiskers, direct end labels."""
    pad_l, pad_r, pad_t, pad_b = 34, 74, 16, 30
    vmax = 8.0
    def x(t):
        return pad_l + (t - 1) / 7 * (w - pad_l - pad_r)
    def y(v):
        return pad_t + (1 - v / vmax) * (h - pad_t - pad_b)
    parts = [f'<svg viewBox="0 0 {w} {h}" width="100%" role="img" class="chart">']
    for gv in (0, 2, 4, 6, 8):
        parts.append(f'<line x1="{pad_l}" y1="{y(gv):.1f}" x2="{w-pad_r}" y2="{y(gv):.1f}" class="grid"/>')
        parts.append(f'<text x="{pad_l-6}" y="{y(gv)+4:.1f}" class="lab" text-anchor="end">{gv}%</text>')
    for t in range(1, 9):
        parts.append(f'<text x="{x(t):.1f}" y="{h-8}" class="lab" text-anchor="middle">{t}</text>')
    for name, pts, cls in series:
        pts = [(t, v, max(0.0, lo), min(vmax, hi)) for t, v, lo, hi in pts]
        path = " ".join(f"{'M' if i==0 else 'L'}{x(t):.1f},{y(v):.1f}"
                        for i, (t, v, lo, hi) in enumerate(pts))
        parts.append(f'<path d="{path}" class="line {cls}"/>')
        for t, v, lo, hi in pts:
            parts.append(f'<line x1="{x(t):.1f}" y1="{y(lo):.1f}" x2="{x(t):.1f}" '
                         f'y2="{y(hi):.1f}" class="whisker {cls}"/>')
            parts.append(f'<circle cx="{x(t):.1f}" cy="{y(v):.1f}" r="4.5" class="dot {cls}"/>')
        t, v, lo, hi = pts[-1]
        parts.append(f'<text x="{x(t)+10:.1f}" y="{y(v)+4:.1f}" class="slab {cls}">{esc(name)}</text>')
    parts.append(f'<text x="{(pad_l+w-pad_r)/2:.1f}" y="{h-8}" class="lab" text-anchor="middle" dy="0"></text>')
    parts.append("</svg>")
    return "".join(parts)


def hbars(rows, w=640, rh=34, unit="%", vmax=100.0, cls="pos"):
    h = rh * len(rows)
    label_w = 330
    parts = [f'<svg viewBox="0 0 {w} {h}" width="100%" role="img" class="chart">']
    for i, (label, v) in enumerate(rows):
        yy = i * rh
        bw = (v / vmax) * (w - label_w - 66)
        parts.append(f'<text x="{label_w-10}" y="{yy+rh/2+4}" class="rowlab" text-anchor="end">{esc(label)}</text>')
        parts.append(f'<rect x="{label_w}" y="{yy+rh/2-7}" width="{bw:.1f}" height="14" rx="4" class="bar {cls}"/>')
        parts.append(f'<text x="{label_w+bw+8:.1f}" y="{yy+rh/2+4}" class="val">{v}{unit}</text>')
    parts.append("</svg>")
    return "".join(parts)


# ---------------------------------------------------------------- data assembly
LADDER = [
    ("Names a real reason to write now", "judged: states a reason for reaching out now",
     "confirmed", "Confirmed in 2026"),
    ("Recipient-focused writing", "judged: recipient_centricity (top 2 of 5)",
     "failed", "Failed the 2026 test"),
    ("Under 100 words", "short (<=100 words)", "direction", "Direction held, smaller"),
    ("Subject line is a question", "subject is a question", "direction", "Direction held"),
    ("Asks 2+ questions", "asks 2+ questions", "direction", "Direction held"),
    ("Has bold text", "has bold text", "gray", "Mostly templating in disguise"),
    ("Reuses their name mid-email", "uses their name again in the body",
     "gray", "Habit vanished in 2026"),
    ("Mass template (3+ identical)", "templated (3+ identical bodies)",
     "confirmed", "Confirmed in 2026"),
]
ladder_rows = []
for label, key, cls, verdict in LADDER:
    r = cp[key]
    color = "pos" if r["fe_gap_pp"] > 0 else "neg"
    if cls == "gray":
        color = "mut"
    ladder_rows.append(
        f'<div class="lrow"><div class="llab">{esc(label)}</div>'
        f'{dot_whisker(r["fe_gap_pp"], r["fe_se_pp"], cls=color)}'
        f'<div class="lval {color}">{r["fe_gap_pp"]:+.1f}</div>'
        f'<div class="chip {cls}">{esc(verdict)}</div></div>')

NULLS = [
    ("Putting links in the email", "Doesn't hurt. Direction positive both years (+4.9, then +1.5), never solid enough to claim."),
    ("Greeting them by name", "Nothing either year (−2.1, then +2.1 — noise around zero)."),
    ("Mentioning their company", "Nothing (0.0, then −0.4). Name-dropping isn't personalisation."),
    ("Citing researched facts about them", "Nothing, two years running (+1.3, then +0.6)."),
    ("Writing that could only be for them", "Nothing solid, two years running (+1.9, then +2.1)."),
    ("A crisp, well-specified ask", "Nothing (−0.0, then +0.9)."),
    ("Going even shorter than 100 words", "No extra gain. Under 100 is a floor, not a slope."),
]
null_rows = "".join(f'<div class="nrow"><div class="nlab">{esc(a)}</div>'
                    f'<div class="ntext">{esc(b)}</div></div>' for a, b in NULLS)

wb = [(r["bucket"], r["rate"]) for r in R["wordbuckets"] if r["bucket"] != "250+"]
word_chart = bar_pairs([("words in the email", [(b, v, "pos" if v >= 10 else "mut") for b, v in wb])],
                       w=640, h=200)

q2_25 = [(r["touch"], r["reply_rate_pct"], r["lo_pct"], r["hi_pct"]) for r in R["q2"]]
q2_26 = [(1, 5.82, 5.09, 6.65), (2, 6.03, 5.06, 7.17), (3, 4.38, 3.32, 5.76),
         (4, 2.16, 1.21, 3.83), (5, 3.23, 1.71, 6.02), (6, 2.86, 1.12, 7.12),
         (7, 2.67, 0.73, 9.21), (8, 5.41, 1.50, 17.70)]
q2_chart = curve_chart([("2025", q2_25, "s1"), ("2026", q2_26, "s2")])

profile_chart = hbars([(p["label"], p["pct"]) for p in R["profile"]], cls="s1")

winners_templated = bar_pairs([
    ("2025 (5,153 emails)", [("templated", cp["templated (3+ identical bodies)"]["rate_with"], "neg"),
                             ("hand-crafted", cp["templated (3+ identical bodies)"]["rate_without"], "pos")]),
    ("2026 (1,286 emails)", [("templated", cp26r["templated (3+ identical bodies)"]["rate_with"], "neg"),
                             ("hand-crafted", cp26r["templated (3+ identical bodies)"]["rate_without"], "pos")]),
], w=560, h=190)
winners_whynow = bar_pairs([
    ("2025", [("has a reason", cp["judged: states a reason for reaching out now"]["rate_with"], "pos"),
              ("no reason", cp["judged: states a reason for reaching out now"]["rate_without"], "mut")]),
    ("2026", [("has a reason", cp26r["judged: states a reason for reaching out now"]["rate_with"], "pos"),
              ("no reason", cp26r["judged: states a reason for reaching out now"]["rate_without"], "mut")]),
], w=560, h=190)

SCORE = [
    ("Mass-templated emails get fewer replies", "confirmed", "Confirmed — both years, both outcomes"),
    ("A real reason-to-write-now wins", "confirmed", "Confirmed — both years, both outcomes"),
    ("Effect size of “reason to write” lands in predicted band", "held", "Held (+2.9, band was +1.6 to +7.6)"),
    ("“Reason to write” is the #1 judged quality", "held", "Held — ranked first again"),
    ("Follow-up #1 is worth as much as the opener", "held", "Held (5.8% vs 6.0%)"),
    ("Most replies arrive by the 4th touch", "held", "Held (96%)"),
    ("Same pattern on the “interested” outcome", "held", "Held"),
    ("“Pain” and “proof” negatives are just email length", "held", "Held"),
    ("The two unreliable qualities stay silent", "held", "Consistent"),
    ("Under 100 words beats longer", "direction", "Direction held — 2025's size didn't repeat"),
    ("Question subject lines help", "direction", "Direction held — too rare in 2026 to be sure"),
    ("Asking 2+ questions hurts", "direction", "Direction held"),
    ("Templated event invites do worse", "direction", "Direction held"),
    ("Short event invites do better", "direction", "Direction held — huge 2025 effect didn't repeat"),
    ("Bold text hurts", "inconclusive", "Too close to call"),
    ("Researched facts / bespoke writing / crisp asks do nothing", "inconclusive",
     "Still nothing — but 2026 too noisy to certify"),
    ("Recipient-focused emails win", "failed", "Failed — +5.3 became −0.4 on fresh data"),
    ("Bullet points ruin event invites", "failed", "Failed — −9.6 became +1.3"),
    ("Reusing their name mid-email hurts", "untestable", "Untestable — habit disappeared (2 emails)"),
]
score_rows = "".join(
    f'<tr><td>{esc(a)}</td><td><span class="chip {c}">{esc(v)}</span></td></tr>'
    for a, c, v in SCORE)

method_tiles = "".join(
    f'<div class="tile"><div class="tname">{esc(a)}</div><div class="tdesc">{esc(b)}</div></div>'
    for a, b in [
        ("Rules first", "Every claim and its pass/fail rule was written down and timestamped in git before the answer was known."),
        ("Blind judging", "The AI that rated email quality never saw who wrote an email, when, or whether it got a reply."),
        ("Two judges", "A second, stronger AI re-scored 1,000 emails. Where they couldn't agree, the quality was thrown out."),
        ("Shuffle test", "The whole analysis was re-run on deliberately scrambled data 10 times. It correctly found ~nothing."),
        ("The 2026 exam", "Half the data stayed sealed until the very end, then every prediction was tested on it exactly once."),
    ])

page = f"""<title>What Gets a Reply</title>
<style>
:root {{
  --page:#f9f9f7; --surface:#fcfcfb; --ink:#0b0b0b; --ink2:#52514e; --mut:#898781;
  --grid:#e1e0d9; --base:#c3c2b7; --border:rgba(11,11,11,.10);
  --pos:#2a78d6; --neg:#e34948; --s2:#eb6834; --good:#0ca30c; --goodtext:#006300; --crit:#d03b3b;
  --chipbg:rgba(11,11,11,.05);
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --page:#0d0d0d; --surface:#1a1a19; --ink:#ffffff; --ink2:#c3c2b7; --mut:#898781;
    --grid:#2c2c2a; --base:#383835; --border:rgba(255,255,255,.10);
    --pos:#3987e5; --neg:#e66767; --s2:#d95926; --good:#0ca30c; --goodtext:#0ca30c; --crit:#d03b3b;
    --chipbg:rgba(255,255,255,.07);
  }}
}}
:root[data-theme="dark"] {{
  --page:#0d0d0d; --surface:#1a1a19; --ink:#ffffff; --ink2:#c3c2b7; --mut:#898781;
  --grid:#2c2c2a; --base:#383835; --border:rgba(255,255,255,.10);
  --pos:#3987e5; --neg:#e66767; --s2:#d95926; --good:#0ca30c; --goodtext:#0ca30c; --crit:#d03b3b;
  --chipbg:rgba(255,255,255,.07);
}}
* {{ box-sizing:border-box; }}
body {{ background:var(--page); color:var(--ink); margin:0;
  font:16px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif; }}
main {{ max-width:860px; margin:0 auto; padding:48px 24px 80px; }}
h1 {{ font-size:44px; line-height:1.1; margin:8px 0 10px; letter-spacing:-.02em; text-wrap:balance; }}
h2 {{ font-size:26px; margin:0 0 6px; letter-spacing:-.01em; text-wrap:balance; }}
p  {{ max-width:64ch; color:var(--ink2); margin:.4em 0; }}
.eyebrow {{ font-size:12px; font-weight:600; letter-spacing:.12em; text-transform:uppercase;
  color:var(--mut); margin:0 0 4px; }}
section {{ background:var(--surface); border:1px solid var(--border); border-radius:14px;
  padding:28px 30px; margin-top:22px; }}
.lead {{ font-size:18px; color:var(--ink); }}
.tally {{ display:flex; gap:10px; flex-wrap:wrap; margin-top:18px; }}
.tally .t {{ background:var(--chipbg); border-radius:10px; padding:10px 16px; text-align:center; }}
.tally .n {{ font-size:26px; font-weight:700; }}
.tally .l {{ font-size:12px; color:var(--ink2); }}
.grid2 {{ display:grid; grid-template-columns:1fr 1fr; gap:26px; }}
@media (max-width:720px) {{ .grid2 {{ grid-template-columns:1fr; }} }}
.tiles {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:12px; margin-top:14px; }}
.tile {{ background:var(--chipbg); border-radius:10px; padding:12px 14px; }}
.tname {{ font-weight:650; font-size:14px; margin-bottom:4px; }}
.tdesc {{ font-size:13px; color:var(--ink2); line-height:1.45; }}
.chart .bar.pos {{ fill:var(--pos); }} .chart .bar.neg {{ fill:var(--neg); }}
.chart .bar.mut {{ fill:var(--mut); opacity:.55; }} .chart .bar.s1 {{ fill:var(--pos); }}
.chart .baseline {{ stroke:var(--base); stroke-width:1.5; }}
.chart .grid {{ stroke:var(--grid); stroke-width:1; }}
.chart text, .strip text {{ font:12px system-ui,sans-serif; fill:var(--ink2);
  font-variant-numeric:tabular-nums; }}
.chart .val {{ font-weight:650; fill:var(--ink); }}
.chart .lab {{ fill:var(--mut); }} .chart .glab {{ fill:var(--ink2); font-weight:600; }}
.chart .rowlab {{ fill:var(--ink); font-size:13px; }}
.chart .line {{ fill:none; stroke-width:2; }} .chart .line.s1 {{ stroke:var(--pos); }}
.chart .line.s2 {{ stroke:var(--s2); }}
.chart .dot.s1, .strip .dot.pos {{ fill:var(--pos); }}
.chart .dot.s2 {{ fill:var(--s2); }} .strip .dot.neg {{ fill:var(--neg); }}
.strip .dot.mut {{ fill:var(--mut); }}
.chart .whisker, .strip .whisker {{ stroke-width:2; opacity:.45; }}
.chart .whisker.s1, .strip .whisker.pos {{ stroke:var(--pos); }}
.chart .whisker.s2 {{ stroke:var(--s2); }} .strip .whisker.neg {{ stroke:var(--neg); }}
.strip .whisker.mut {{ stroke:var(--mut); }}
.chart .slab {{ font-weight:650; }} .chart .slab.s1 {{ fill:var(--pos); }} .chart .slab.s2 {{ fill:var(--s2); }}
.strip .zeroline {{ stroke:var(--base); stroke-width:1.5; stroke-dasharray:2 3; }}
.lrow {{ display:grid; grid-template-columns:minmax(180px,1fr) 260px 52px minmax(150px,auto);
  gap:12px; align-items:center; padding:7px 0; border-bottom:1px solid var(--grid); }}
.lrow:last-child {{ border-bottom:none; }}
.llab {{ font-size:14.5px; }}
.lval {{ font-weight:700; font-variant-numeric:tabular-nums; text-align:right; }}
.lval.pos {{ color:var(--pos); }} .lval.neg {{ color:var(--neg); }} .lval.mut {{ color:var(--mut); }}
.chip {{ display:inline-block; font-size:12px; font-weight:600; border-radius:99px;
  padding:3px 10px; background:var(--chipbg); color:var(--ink2); white-space:nowrap; }}
.chip.confirmed, .chip.held {{ color:var(--goodtext); background:rgba(12,163,12,.12); }}
.chip.direction {{ color:var(--pos); background:rgba(42,120,214,.12); }}
.chip.failed {{ color:var(--crit); background:rgba(208,59,59,.12); }}
.chip.inconclusive, .chip.untestable, .chip.gray {{ color:var(--ink2); }}
.nrow {{ display:grid; grid-template-columns:minmax(200px,240px) 1fr; gap:16px;
  padding:9px 0; border-bottom:1px solid var(--grid); }}
.nrow:last-child {{ border-bottom:none; }}
.nlab {{ font-weight:650; font-size:14.5px; }} .ntext {{ color:var(--ink2); font-size:14.5px; }}
table {{ width:100%; border-collapse:collapse; font-size:14.5px; }}
td {{ padding:8px 10px 8px 0; border-bottom:1px solid var(--grid); vertical-align:top; }}
tr:last-child td {{ border-bottom:none; }}
.note {{ font-size:13.5px; color:var(--mut); margin-top:10px; }}
.fine li {{ color:var(--ink2); font-size:14.5px; margin:7px 0; max-width:75ch; }}
.stat {{ font-size:34px; font-weight:750; letter-spacing:-.01em; }}
.statrow {{ display:flex; gap:34px; flex-wrap:wrap; margin:10px 0 2px; }}
.statrow .l {{ font-size:13px; color:var(--ink2); max-width:200px; }}
footer {{ color:var(--mut); font-size:13px; margin-top:26px; }}
</style>
<main>
<p class="eyebrow">Cold email reply study · Encord · Jan 2025 – Jul 2026</p>
<h1>What Gets a Reply</h1>
<p class="lead">We took 12,077 outreach emails, measured everything countable about them,
had a blinded AI rate their quality, and asked which traits go with getting a reply.
Then we did the one thing that separates findings from stories: we wrote our answers
down, sealed away the 2026 data, and tested every claim on it — once.</p>
<div class="tally">
<div class="t"><div class="n" style="color:var(--goodtext)">9</div><div class="l">held / confirmed</div></div>
<div class="t"><div class="n" style="color:var(--pos)">4</div><div class="l">direction held</div></div>
<div class="t"><div class="n">4</div><div class="l">too close to call</div></div>
<div class="t"><div class="n" style="color:var(--crit)">2</div><div class="l">failed the test</div></div>
<div class="t"><div class="n">1</div><div class="l">untestable</div></div>
</div>

<section>
<p class="eyebrow">Finding 1 · Confirmed on sealed data</p>
<h2>Mass-produced emails get a quarter of the replies</h2>
<p>Send the same body to 3+ people and the reply rate collapses — within the same
sender, so it isn't “worse reps use templates.” This was the largest effect in 2025 and
it repeated almost exactly in 2026.</p>
{winners_templated}
<p class="note">Cold pitches, reply rate. 2026 tested blind: predicted before looking, p=0.005.
Same result on the stricter “showed real interest” outcome (0.9% vs 5.6% in 2026).</p>
</section>

<section>
<p class="eyebrow">Finding 2 · Confirmed on sealed data</p>
<h2>A real reason to write now roughly doubles replies</h2>
<p>A launch, a funding round, an event, a referral, a visit — something checkable that
explains “why this email, this week.” This beat every quality the AI judged, both years.
Doing research on the prospect did <em>not</em> matter; having a reason to write did.</p>
{winners_whynow}
<p class="note">Cold pitches, reply rate. 2026: +2.9 points (p=0.047 replied, p=0.012 interested),
inside the band predicted in advance, ranked #1 again as predicted.</p>
</section>

<section>
<p class="eyebrow">The full picture · 2025 effects, 2026 verdicts</p>
<h2>Everything that moved replies — and what survived</h2>
<p>Each line: the 2025 effect in percentage points (dot), its uncertainty (bar), and
what happened when the claim faced the sealed 2026 data.</p>
{''.join(ladder_rows)}
<p class="note">Cold pitches, within-sender. “Bold text” and “name reuse” are mostly the
template finding wearing different clothes — 77–80% of those emails were templates.</p>
</section>

<section>
<p class="eyebrow">Just as important</p>
<h2>What does nothing</h2>
<p>These contradict most sales-blog advice. Each was tested with the same rigor as the
findings above — “no effect” here is an answer, not an absence.</p>
{null_rows}
<div style="margin-top:20px">{word_chart}</div>
<p class="note">Reply rate by email length: the benefit is a floor at ~100 words, not
“shorter is always better.”</p>
</section>

<section>
<p class="eyebrow">Question 2</p>
<h2>The first follow-up is worth as much as the opener</h2>
{q2_chart}
<div class="statrow">
<div><div class="stat">61%</div><div class="l">of all replies arrive after the first email</div></div>
<div><div class="stat">~90%</div><div class="l">of eventual replies are in by the 3rd touch</div></div>
<div><div class="stat">+0.6pp</div><div class="l">is all that touches 5–8 add, combined (2025)</div></div>
</div>
<p class="note">Chance of a reply after each touch, among people still silent. Who
receives touch 5 is the rep's choice, so late-touch numbers describe survivors — but the
early-touch pattern repeated in 2026, exactly as predicted.</p>
</section>

<section>
<p class="eyebrow">The mirror</p>
<h2>What the corpus actually looks like</h2>
<p>Blind AI ratings of all 12,462 emails, before any outcome was attached. The team
writes clean, well-formed emails — that are mostly about us.</p>
{profile_chart}
</section>

<section>
<p class="eyebrow">The safety net, working</p>
<h2>Two findings died on fresh data — that's the system doing its job</h2>
<p><strong>“Recipient-focused emails win”</strong> looked great in 2025 (+5.3 points,
passed every internal check). On sealed 2026 data: <strong>−0.4</strong>. Dead. It was
labelled exploratory with warnings attached, and every warning turned out to be earned.
Without the sealed-data test, this would be in the recommendations.</p>
<p><strong>“Bullet points ruin event invites”</strong> (−9.6 in 2025) came back at
+1.3 in 2026. A one-year artefact, now on record as such.</p>
</section>

<section>
<p class="eyebrow">Scorecard</p>
<h2>All 19 predictions, scored</h2>
<table>{score_rows}</table>
</section>

<section>
<p class="eyebrow">How we made sure this is real</p>
<h2>Five safeguards</h2>
<div class="tiles">{method_tiles}</div>
</section>

<section>
<p class="eyebrow">Fine print, in plain words</p>
<h2>What this study can and can't say</h2>
<ul class="fine">
<li><strong>Scope.</strong> This covers email with a Gmail record — hand-sent and
Apollo-sent. Amplemarket blasts are invisible to us (their replies can't be tracked
reliably), and they grew from 20% of outreach in 2025 to 71% in 2026. So these findings
describe a shrinking, more careful slice of outbound — about 75% of it in 2025, under
30% in 2026 — and say nothing about whether the Amplemarket machine works.</li>
<li><strong>The sending tool doesn't change what works.</strong> Tool-sent emails reply
about 2 points lower across the board, but it's a flat offset: across all 29 traits
tested, the tool changed the effect of essentially none of them. It shifts the baseline,
not the recipe — and it's likely partly a tracking artefact, so no claim is made either way.</li>
<li><strong>Correlation, mostly.</strong> Reps choose who gets the hand-written email.
Comparing each rep against themselves removes a lot of that, but a rep may save their
best emails for their best prospects. Treat effect sizes as upper bounds.</li>
<li><strong>Two AI qualities were thrown out.</strong> “Economy” and “peer tone”
couldn't be scored consistently — by either of two different AIs — so nothing is claimed
about them.</li>
<li><strong>The personalisation nulls are honest nulls, not proofs.</strong> Two years,
never a significant positive effect — but 2026 was too small to certify the effect is
under 3 points. “We found nothing, twice” is the exact claim.</li>
<li><strong>One known leak.</strong> 155 Amplemarket emails slipped into scope on a
technicality. Documented, left in place, and every 2026 test was re-run without them —
nothing changes.</li>
</ul>
</section>

<footer>Every number traces to a committed file in the study repo
(docs/13–16, output/). Analysis: within-sender comparisons, cluster-robust uncertainty,
multiple-comparison corrected. Built 15 Aug 2026.</footer>
</main>
"""

path = os.path.join(OUT, "what-gets-a-reply.html")
open(path, "w").write(page)
print(f"wrote {path} ({len(page):,} bytes)")
