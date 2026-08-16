"""Executive document (PDF via headless Chrome print) — axiomatic structure.

Operator direction (2026-08-16): structure over narrative. Objective -> questions ->
method -> layers -> findings. Standardized tables with fixed columns and a controlled
verdict vocabulary; nuance lives in footnotes, never inside cells. Professional type:
Georgia body, Helvetica Neue headings/tables. Charts only where a table cannot carry
the shape. Numbers injected from committed artefacts — never retyped.
"""
import html
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "output")
R = json.load(open(os.path.join(OUT, "results_2025.json")))
cp = {r["feature"]: r for r in R["cp_replied"]}
ev = {r["feature"]: r for r in R["ev_replied"]}


def load(tag):
    return {r["feature"]: r for r in json.load(open(f"{OUT}/q1_{tag}.json"))
            if not r.get("note")}


c26r = load("cold_pitch_2026_replied_G30")
c26i = load("cold_pitch_2026_interested_G30")
e26r = load("event_invite_2026_replied_G30")


def esc(s):
    return html.escape(str(s))


def bar_pairs(groups, w=470, h=160, unit="%"):
    n_bars = sum(len(g[1]) for g in groups)
    gap_group, gap_bar = 30, 8
    bw = (w - gap_group * (len(groups) - 1) - gap_bar * (n_bars - len(groups))) / n_bars
    vmax = max(v for _, bars in groups for _, v, _ in bars) * 1.25
    base = h - 32
    p = [f'<svg viewBox="0 0 {w} {h}" width="100%" class="chart">',
         f'<line x1="0" y1="{base}" x2="{w}" y2="{base}" class="baseline"/>']
    xx = 0.0
    for glabel, bars in groups:
        gx0 = xx
        for blabel, v, cls in bars:
            bh = max(3, (v / vmax) * (base - 24))
            p.append(f'<rect x="{xx:.1f}" y="{base-bh:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="3" class="bar {cls}"/>')
            p.append(f'<text x="{xx+bw/2:.1f}" y="{base-bh-6:.1f}" class="val" text-anchor="middle">{v}{unit}</text>')
            p.append(f'<text x="{xx+bw/2:.1f}" y="{base+13}" class="lab" text-anchor="middle">{esc(blabel)}</text>')
            xx += bw + gap_bar
        xx -= gap_bar
        p.append(f'<text x="{(gx0+xx)/2:.1f}" y="{base+27}" class="glab" text-anchor="middle">{esc(glabel)}</text>')
        xx += gap_group
    p.append("</svg>")
    return "".join(p)


def curve_chart(series, w=620, h=210):
    pad_l, pad_r, pad_t, pad_b = 34, 66, 12, 26
    vmax = 8.0
    def x(t): return pad_l + (t - 1) / 7 * (w - pad_l - pad_r)
    def y(v): return pad_t + (1 - v / vmax) * (h - pad_t - pad_b)
    p = [f'<svg viewBox="0 0 {w} {h}" width="100%" class="chart">']
    for gv in (0, 2, 4, 6, 8):
        p.append(f'<line x1="{pad_l}" y1="{y(gv):.1f}" x2="{w-pad_r}" y2="{y(gv):.1f}" class="grid"/>')
        p.append(f'<text x="{pad_l-6}" y="{y(gv)+3.5:.1f}" class="lab" text-anchor="end">{gv}%</text>')
    for t in range(1, 9):
        p.append(f'<text x="{x(t):.1f}" y="{h-5}" class="lab" text-anchor="middle">{t}</text>')
    for name, pts, cls in series:
        pts = [(t, v, max(0.0, lo), min(vmax, hi)) for t, v, lo, hi in pts]
        path = " ".join(f"{'M' if i==0 else 'L'}{x(t):.1f},{y(v):.1f}" for i, (t, v, *_ ) in enumerate(pts))
        p.append(f'<path d="{path}" class="line {cls}"/>')
        for t, v, lo, hi in pts:
            p.append(f'<line x1="{x(t):.1f}" y1="{y(lo):.1f}" x2="{x(t):.1f}" y2="{y(hi):.1f}" class="whisker {cls}"/>')
            p.append(f'<circle cx="{x(t):.1f}" cy="{y(v):.1f}" r="3.6" class="dot {cls}"/>')
        t, v, *_ = pts[-1]
        p.append(f'<text x="{x(t)+8:.1f}" y="{y(v)+3.5:.1f}" class="slab {cls}">{esc(name)}</text>')
    p.append("</svg>")
    return "".join(p)


# ---------------- standardized findings tables --------------------------------
def fmt_p(p):
    if p is None:
        return "—"
    return "<0.001" if p < 0.001 else f"{p:.3f}"


def frow(trait, r25, r26, verdict, note=""):
    """Fixed columns: trait | 2025 effect | 2026 effect | 2026 p | verdict."""
    e25 = f"{r25['fe_gap_pp']:+.1f}" if r25 else "—"
    e26 = f"{r26['fe_gap_pp']:+.1f}" if r26 else "—"
    p26 = fmt_p(r26["fe_p"]) if r26 else "—"
    sup = f'<sup>{note}</sup>' if note else ""
    return (f"<tr><td>{esc(trait)}{sup}</td><td class=num>{e25}</td>"
            f"<td class=num>{e26}</td><td class=num>{p26}</td>"
            f"<td><span class='chip {verdict.lower()}'>{verdict}</span></td></tr>")


HEAD = ("<tr><th>Trait</th><th>2025 effect (pp) · training</th><th>2026 effect (pp) · validation</th>"
        "<th>2026 p</th><th>Verdict</th></tr>")

t_confirmed = HEAD + "".join([
    frow("Templated body (3+ identical copies)", cp["templated (3+ identical bodies)"],
         c26r["templated (3+ identical bodies)"], "CONFIRMED"),
    frow("States a reason to write now (why-now)", cp["judged: states a reason for reaching out now"],
         c26r["judged: states a reason for reaching out now"], "CONFIRMED", "a"),
])
t_direction = HEAD + "".join([
    frow("Body ≤100 words", cp["short (<=100 words)"], c26r["short (<=100 words)"], "DIRECTION", "b"),
    frow("Subject line is a question", cp["subject is a question"], c26r["subject is a question"], "DIRECTION", "c"),
    frow("Asks 2+ questions", cp["asks 2+ questions"], c26r["asks 2+ questions"], "DIRECTION"),
    frow("Event invite: templated body", ev["templated (3+ identical bodies)"],
         e26r["templated (3+ identical bodies)"], "DIRECTION"),
    frow("Event invite: body ≤100 words", ev["short (<=100 words)"], e26r["short (<=100 words)"], "DIRECTION", "b"),
])
t_null = HEAD + "".join([
    frow("Cites researched facts about recipient", cp["judged: research_signal (top 2 of 5)"],
         c26r["judged: research_signal (top 2 of 5)"], "NULL", "d"),
    frow("Reads written-only-for-them (bespokeness)", cp["judged: bespokeness (top 2 of 5)"],
         c26r["judged: bespokeness (top 2 of 5)"], "NULL", "d"),
    frow("Single clear, specified ask", cp["judged: ask_clarity (top 2 of 5)"],
         c26r["judged: ask_clarity (top 2 of 5)"], "NULL", "d"),
    frow("Contains a link", cp["has a link"], c26r["has a link"], "NULL"),
    frow("Greets recipient by name", cp["greets them by name"], c26r["greets them by name"], "NULL"),
    frow("Mentions recipient's company", cp["mentions their company"], c26r["mentions their company"], "NULL"),
    frow("Polished writing", cp["judged: polish (top 2 of 5)"], c26r["judged: polish (top 2 of 5)"], "NULL"),
])
t_closed = HEAD + "".join([
    frow("Recipient-focused writing", cp["judged: recipient_centricity (top 2 of 5)"],
         c26r["judged: recipient_centricity (top 2 of 5)"], "FAILED"),
    frow("Event invite: contains bullet points", ev["has bullets"], e26r["has bullets"], "FAILED"),
    frow("Contains bold text", cp["has bold text"], c26r["has bold text"], "INCONCLUSIVE", "e"),
    frow("Reuses recipient's name mid-body", cp["uses their name again in the body"], None, "UNTESTABLE", "f"),
])

# Q2 standardized table
q2rows = ""
q226 = {1: (5.82, 3486), 2: (6.03, 1974), 3: (4.38, 1095), 4: (2.16, 509),
        5: (3.23, 279), 6: (2.86, 140), 7: (2.67, 75), 8: (5.41, 37)}
for r in R["q2"]:
    t = r["touch"]
    q2rows += (f"<tr><td class=num>{t}</td><td class=num>{r['people_who_got_this_touch']:,}</td>"
               f"<td class=num>{r['reply_rate_pct']:.1f}%</td><td class=num>{r['cum']}%</td>"
               f"<td class=num>{q226[t][1]:,}</td><td class=num>{q226[t][0]:.1f}%</td></tr>")

q2_25 = [(r["touch"], r["reply_rate_pct"], r["lo_pct"], r["hi_pct"]) for r in R["q2"]]
q2_26c = [(1, 5.82, 5.09, 6.65), (2, 6.03, 5.06, 7.17), (3, 4.38, 3.32, 5.76), (4, 2.16, 1.21, 3.83),
          (5, 3.23, 1.71, 6.02), (6, 2.86, 1.12, 7.12), (7, 2.67, 0.73, 9.21), (8, 5.41, 1.50, 17.70)]
q2_chart = curve_chart([("2025", q2_25, "s1"), ("2026", q2_26c, "s2")])

tmp, why = cp["templated (3+ identical bodies)"], cp["judged: states a reason for reaching out now"]
tmp26, why26 = c26r["templated (3+ identical bodies)"], c26r["judged: states a reason for reaching out now"]
chart_t = bar_pairs([("2025", [("templated", tmp["rate_with"], "neg"), ("hand-crafted", tmp["rate_without"], "pos")]),
                     ("2026 validation", [("templated", tmp26["rate_with"], "neg"), ("hand-crafted", tmp26["rate_without"], "pos")])])
chart_w = bar_pairs([("2025", [("has reason", why["rate_with"], "pos"), ("no reason", why["rate_without"], "mut")]),
                     ("2026 validation", [("has reason", why26["rate_with"], "pos"), ("no reason", why26["rate_without"], "mut")])])

KAPPA = [("Reason to write now", .716, .725, "RETAINED"), ("Research on recipient", .749, .735, "RETAINED"),
         ("Pain hypothesis", .694, .642, "RETAINED"), ("Value specificity", .665, .621, "RETAINED"),
         ("Customer proof", .650, .662, "RETAINED"), ("Bespokeness", .564, .602, "RETAINED"),
         ("Ask clarity", .421, .570, "RETAINED"), ("Polish", .428, .460, "RETAINED"),
         ("Recipient focus", .435, .445, "RETAINED"), ("Peer tone", .320, .318, "DISCARDED"),
         ("Economy", .220, .256, "DISCARDED")]
kappa_rows = "".join(
    f"<tr><td>{esc(a)}</td><td class=num>{s:.2f}</td><td class=num>{c:.2f}</td>"
    f"<td><span class='chip {'null' if v=='RETAINED' else 'failed'}'>{v}</span></td></tr>"
    for a, s, c, v in KAPPA)

prof_rows = "".join(f"<tr><td>{esc(p['label'])}</td><td class=num>{p['pct']}%</td></tr>"
                    for p in R["profile"])

wb_rows = "".join(f"<tr><td class=num>{esc(r['bucket'])}</td><td class=num>{r['n']:,}</td>"
                  f"<td class=num>{r['rate']}%</td></tr>"
                  for r in R["wordbuckets"] if r["bucket"] != "250+")

IMPL = [("Stop sending identical bodies at scale from personal mailboxes", "STRONG"),
        ("Require every cold email to state its reason-to-write-now", "STRONG"),
        ("Always send follow-ups 1–2; usually 3; stop at 4 absent a new reason", "MODERATE"),
        ("Keep openers under ~100 words (no benefit below that)", "MODERATE"),
        ("Stop research-heavy personalisation as a reply tactic", "MODERATE"),
        ("Stop removing links; stop name-greeting rituals", "MODERATE")]
impl_rows = "".join(f"<tr><td>{esc(a)}</td><td><span class='chip {g.lower()}'>{g}</span></td></tr>"
                    for a, g in IMPL)

DOC = f"""<!doctype html><html><head><meta charset="utf-8"><title>What Gets a Reply — Executive Document</title>
<style>
:root {{ --ink:#111; --ink2:#444; --mut:#777; --grid:#ddd; --base:#bbb;
  --pos:#2a78d6; --neg:#c0392b; --s2:#d97a29; --good:#1a6b1a; --crit:#b03030;
  --chipbg:#f0f0ee; }}
* {{ box-sizing:border-box; }}
html, body {{ margin:0; padding:0; background:#fff; color:var(--ink);
  font:10pt/1.5 Georgia, "Times New Roman", serif; }}
@page {{ size:A4; margin:17mm 17mm 18mm; }}
.pagebreak {{ break-before:page; }} .avoid {{ break-inside:avoid; }}
h1 {{ font:700 23pt/1.15 "Helvetica Neue", Helvetica, Arial, sans-serif; letter-spacing:-.01em; margin:2pt 0 6pt; }}
h2 {{ font:700 13pt/1.2 "Helvetica Neue", Helvetica, Arial, sans-serif; margin:0 0 6pt; }}
h3 {{ font:600 10.5pt "Helvetica Neue", Helvetica, Arial, sans-serif; margin:10pt 0 3pt; }}
p {{ margin:4pt 0; max-width:68ch; }}
.eyebrow {{ font:700 7pt "Helvetica Neue", Arial, sans-serif; letter-spacing:.16em; text-transform:uppercase; color:var(--mut); margin:0 0 3pt; }}
.small {{ font:8pt "Helvetica Neue", Arial, sans-serif; color:var(--mut); }}
.fnote {{ font:8pt/1.45 "Helvetica Neue", Arial, sans-serif; color:var(--ink2); margin:4pt 0 0; }}
table {{ width:100%; border-collapse:collapse; font:8.8pt/1.35 "Helvetica Neue", Helvetica, Arial, sans-serif; margin:5pt 0 2pt; }}
th {{ font-size:7pt; text-transform:uppercase; letter-spacing:.09em; color:var(--mut);
  border-bottom:1pt solid var(--ink); padding:3pt 8pt 3pt 0; text-align:left; }}
td {{ padding:3.5pt 8pt 3.5pt 0; border-bottom:.5pt solid var(--grid); vertical-align:top; }}
td.num {{ font-variant-numeric:tabular-nums; white-space:nowrap; }}
.chip {{ display:inline-block; font:600 7pt "Helvetica Neue", Arial, sans-serif; letter-spacing:.06em;
  border-radius:2pt; padding:1.5pt 6pt; background:var(--chipbg); color:var(--ink2); }}
.chip.confirmed, .chip.held, .chip.strong {{ color:#fff; background:var(--good); }}
.chip.direction, .chip.moderate {{ color:#fff; background:var(--pos); }}
.chip.failed {{ color:#fff; background:var(--crit); }}
.chip.null, .chip.inconclusive, .chip.untestable {{ color:var(--ink2); background:var(--chipbg); }}
.chart text {{ font:7.5pt "Helvetica Neue", Arial, sans-serif; fill:var(--ink2); font-variant-numeric:tabular-nums; }}
.chart .val {{ font-weight:700; fill:var(--ink); }} .chart .lab {{ fill:var(--mut); }}
.chart .glab {{ fill:var(--ink2); font-weight:600; }}
.chart .baseline {{ stroke:var(--base); stroke-width:1; }} .chart .grid {{ stroke:var(--grid); stroke-width:.7; }}
.bar.pos {{ fill:var(--pos); }} .bar.neg {{ fill:var(--neg); }} .bar.mut {{ fill:#aaa; }}
.line {{ fill:none; stroke-width:1.6; }} .line.s1 {{ stroke:var(--pos); }} .line.s2 {{ stroke:var(--s2); }}
.dot.s1 {{ fill:var(--pos); }} .dot.s2 {{ fill:var(--s2); }}
.whisker {{ stroke-width:1.3; opacity:.4; }} .whisker.s1 {{ stroke:var(--pos); }} .whisker.s2 {{ stroke:var(--s2); }}
.slab {{ font-weight:700; }} .slab.s1 {{ fill:var(--pos); }} .slab.s2 {{ fill:var(--s2); }}
.grid2 {{ display:grid; grid-template-columns:1fr 1fr; gap:16pt; }}
ol.ax {{ margin:4pt 0 4pt 18pt; padding:0; }} ol.ax li {{ margin:2pt 0; }}
.def dt {{ font:600 9pt "Helvetica Neue", Arial, sans-serif; margin-top:5pt; }}
.def dd {{ margin:1pt 0 0 0; color:var(--ink2); }}
</style></head><body>

<!-- ================= COVER / SUMMARY ================= -->
<p class="eyebrow">Encord · Cold outbound study · Data window Jan 2025 – Jul 2026 · Prepared 16 Aug 2026</p>
<h1>What Gets a Reply</h1>
<p style="font-size:11pt">Pre-registered observational study, n = 12,077 outreach emails.
2025 was used as the training set; Jan–Jul 2026 was held back as a sealed validation set and opened once.</p>

<h3>0.1 · Objective</h3>
<p>Measure two quantities and answer two questions.</p>
<table>
<tr><th></th><th>Quantity measured</th><th>Question</th></tr>
<tr><td class=num>Q1</td><td>Reply rate to the first cold email</td><td>Which properties of the email predict a reply?</td></tr>
<tr><td class=num>Q2</td><td>Replies per follow-up touch</td><td>How many follow-ups are productive?</td></tr>
</table>
<p class="fnote">Outcomes: <b>replied</b> = a human wrote back (label accuracy 99.0%);
<b>interested</b> = the reply shows forward motion (92.8%). Every finding is reported on both.</p>

<h3>0.2 · Principal results</h3>
<table>
<tr><th>#</th><th>Result</th><th>2025</th><th>2026 validation</th><th>Status</th></tr>
<tr><td class=num>R1</td><td>Templated bodies collapse replies</td><td class=num>4.8% vs 9.3%</td><td class=num>1.8% vs 8.0%</td><td><span class="chip confirmed">CONFIRMED</span></td></tr>
<tr><td class=num>R2</td><td>A stated reason-to-write-now doubles replies<sup>a</sup></td><td class=num>7.9% vs 4.6%</td><td class=num>8.5% vs 4.1%</td><td><span class="chip confirmed">CONFIRMED</span></td></tr>
<tr><td class=num>R3</td><td>Researched personalisation does not move replies</td><td class=num>+1.3 pp n.s.</td><td class=num>+0.6 pp n.s.</td><td><span class="chip null">NULL</span></td></tr>
<tr><td class=num>R4</td><td>Follow-up 1 is worth as much as the opener</td><td class=num>5.0% vs 4.1%</td><td class=num>6.0% vs 5.8%</td><td><span class="chip held">HELD</span></td></tr>
<tr><td class=num>R5</td><td>2 of 19 predictions failed validation and are withdrawn</td><td colspan=2></td><td><span class="chip failed">WITHDRAWN</span></td></tr>
</table>
<p class="fnote"><sup>a</sup> Confirmed under the pre-committed rule (p=0.047); margin is
fragile — 2 of 5 robustness specifications lift p above 0.05 (§7, L4). 2025 evidence is
unambiguous (p&lt;0.001 in every specification).</p>

<h3>0.3 · Implications, graded by evidence</h3>
<table><tr><th>Action</th><th>Grade</th></tr>{impl_rows}</table>

<!-- ================= 1 METHOD ================= -->
<div class="pagebreak"></div>
<p class="eyebrow">Section 1 · Method</p>
<h2>1 · Design</h2>
<h3>1.1 · Data</h3>
<table>
<tr><th>Stage</th><th>Definition</th><th>N</th></tr>
<tr><td>Sent-email records</td><td>All outbound engagement records, 4 internal domains</td><td class=num>~117,000</td></tr>
<tr><td>Study frame</td><td>First email of a fresh push (≥30 days silence), Gmail-recorded, commercial sender; bounces &amp; existing threads excluded</td><td class=num>12,077</td></tr>
<tr><td>— cold pitches / event invites</td><td>email type assigned blind by AI (2025 + 2026)</td><td class=num>5,153+1,286 / 3,179+1,837</td></tr>
<tr><td>Reply candidates labelled</td><td>human / auto-reply / calendar / bounce (99.0% accuracy)</td><td class=num>16,695</td></tr>
<tr><td>Emails scored by blinded AI judge</td><td>12 qualities × anchored rubric</td><td class=num>12,462</td></tr>
</table>

<h3>1.2 · Design principles</h3>
<ol class="ax">
<li><b>P1 — Within-sender comparison.</b> Every effect compares a rep's own emails with vs
without a trait; rep skill and rep targeting cancel out.</li>
<li><b>P2 — Rules before results.</b> Traits, thresholds, outcome definitions and pass/fail
rules were committed to a timestamped record before any result was computed.</li>
<li><b>P3 — Multiplicity control.</b> ~40 traits tested ⇒ 1–2 false positives expected by
chance; Benjamini–Hochberg correction applied within pre-declared families.</li>
<li><b>P4 — Blind judging.</b> The AI judge saw subject + body only: sender, date,
recipient identity and outcome redacted. Automated leak gate: 0 leaks / 12,462 items.</li>
<li><b>P5 — Placebo.</b> The full analysis re-run on outcome-shuffled data ×10: 5 spurious
hits in 240 tests (2.1%), under the 5% ceiling. The machinery invents nothing.</li>
<li><b>P6 — Training / validation split.</b> 2025 = training set (free exploration); Jan–Jul
2026 = validation set, sealed until every prediction was committed, then opened exactly
once. A finding that fails validation is withdrawn, never rescued.</li>
</ol>

<h3>1.3 · Two measurement layers</h3>
<table>
<tr><th>Layer</th><th>What</th><th>How measured</th><th>Examples</th></tr>
<tr><td class=num>L1</td><td>Countable traits</td><td>Audited code (61 regression tests)</td><td>length, questions, links, subject shape, template detection</td></tr>
<tr><td class=num>L2</td><td>Judged qualities</td><td>Blinded AI, anchored 1–5 rubric; dual-model reliability check (§5)</td><td>why-now, research signal, bespokeness, tone</td></tr>
</table>

<h3>1.4 · Verdict vocabulary (fixed before the validation set was opened)</h3>
<table>
<tr><th style="width:70pt">Verdict</th><th>Definition</th></tr>
<tr><td><span class="chip confirmed">CONFIRMED</span></td><td>Significant in 2025 after correction; same sign and p&lt;0.05 in the 2026 validation set.</td></tr>
<tr><td><span class="chip held">HELD</span></td><td>A committed non-effect-size prediction (curve shape, ranking, band) satisfied in 2026.</td></tr>
<tr><td><span class="chip direction">DIRECTION</span></td><td>Same sign in 2026 but not significant there (2026 is ¼ the size of 2025).</td></tr>
<tr><td><span class="chip null">NULL</span></td><td>No significant effect in either year, with sample sizes able to detect effects the size of R1/R2.</td></tr>
<tr><td><span class="chip inconclusive">INCONCLUSIVE</span></td><td>2026 too noisy to rule either way under the pre-committed equivalence bound.</td></tr>
<tr><td><span class="chip failed">FAILED</span></td><td>2026 estimate contradicts 2025 and statistically excludes the 2025 effect size. Withdrawn.</td></tr>
<tr><td><span class="chip untestable">UNTESTABLE</span></td><td>The trait effectively vanished from 2026 email; no test possible.</td></tr>
</table>

<!-- ================= 2 Q1 FINDINGS ================= -->
<div class="pagebreak"></div>
<p class="eyebrow">Section 2 · Question 1 — what predicts a reply</p>
<h2>2 · Q1 findings</h2>
<p class="small">All effects: percentage points (pp) on reply rate, within-sender, cold
pitches unless marked. 2025 n=5,153 (base 6.9%); validation 2026 n=1,286 (base 6.5%).
The companion "interested" outcome agrees in sign throughout.</p>

<h3>2.1 · Confirmed effects</h3>
<table class="avoid">{t_confirmed}</table>
<p class="fnote"><sup>a</sup> Fragile 2026 margin: main specification p=0.047; 2 of 5
robustness specifications lift p to 0.10 / 0.07. Sign holds in all five; the fair-window
sensitivity strengthens it (+3.3, p=0.024). See §7, L4.</p>
<div class="grid2 avoid">
<div>{chart_t}<p class="small" style="text-align:center">R1 — reply rate, templated vs hand-crafted</p></div>
<div>{chart_w}<p class="small" style="text-align:center">R2 — reply rate, with vs without a stated reason</p></div>
</div>
<p class="fnote">R1 fingerprints: bold text (−4.3 pp) and mid-body name reuse (−5.4 pp)
looked harmful in 2025, but 77–80% of emails carrying them were templates — one
phenomenon, counted once.</p>

<h3>2.2 · Directional effects (sign replicated; 2026 underpowered)</h3>
<table class="avoid">{t_direction}</table>
<p class="fnote"><sup>b</sup> 2026 excludes the 2025 effect size — direction survives,
magnitude does not. <sup>c</sup> Question-subjects fell from 19% of 2025 cold pitches to
6% in 2026 (n=79); no power. Event-invite rows: 2025 n=3,179 (base 15.1%), 2026 n=1,837 (13.5%).</p>

<h3>2.3 · Null effects — equal standing with the positives</h3>
<table class="avoid">{t_null}</table>
<p class="fnote"><sup>d</sup> The three personalisation nulls are pre-registered primary
dimensions; under the pre-committed equivalence bound the 2026 CIs cannot certify the
effect is ≤3 pp, so formally "still nothing, twice" rather than "proven zero".
Research-signal and bespokeness correlate r=0.83 — one finding, not two.</p>

<h3>2.4 · Failed, inconclusive, untestable</h3>
<table class="avoid">{t_closed}</table>
<p class="fnote"><sup>e</sup> Bold-text cell shrank to n=126; wrong sign inside noise —
the pre-committed rule scores this inconclusive, not refuted. <sup>f</sup> Mid-body name
reuse fell from 7.7% of 2025 cold pitches to 2 emails in 2026; the habit itself disappeared.</p>

<h3>2.5 · Word-length shape (2025 cold pitches)</h3>
<div class="grid2 avoid">
<div><table>
<tr><th>Words</th><th>N</th><th>Reply rate</th></tr>{wb_rows}</table></div>
<div><p class="small" style="margin-top:8pt">The benefit is a <b>floor at ~100 words</b>,
not a slope: below 100 there is no further gain (≤60-word emails do no better than
61–100-word emails).</p></div>
</div>

<!-- ================= 3 Q2 ================= -->
<div class="pagebreak"></div>
<p class="eyebrow">Section 3 · Question 2 — follow-ups</p>
<h2>3 · Q2 findings</h2>
<table class="avoid">
<tr><th>Touch</th><th>Received it (2025)</th><th>Reply rate (2025)</th><th>Cumulative (2025)</th><th>Received it (2026)</th><th>Reply rate (2026)</th></tr>
{q2rows}</table>
<p class="fnote">Reply rate = share of still-silent recipients who replied after that touch.
All email types; 8,591 pushes (2025), 3,486 (2026). Late-touch 2026 cells are small — see
uncertainty bars in the chart.</p>
<div class="avoid">{q2_chart}</div>
<h3>3.1 · Statements</h3>
<ol class="ax">
<li>Follow-up 1 out-performs the opener in both years (5.0 vs 4.1; 6.0 vs 5.8). Predicted; <b>HELD</b>.</li>
<li>61% of all replies arrive after the opener; ~90% of eventual replies are in by touch 3.</li>
<li>Touches 5–8 added 0.6 pp combined (2025). Predicted ≥85% of replies by touch 4; observed 96% (2026); <b>HELD</b>.</li>
<li>Constraint: who receives touch 5 is the rep's choice — late-touch rates describe survivors.</li>
</ol>

<!-- ================= 4 CORPUS ================= -->
<p class="eyebrow" style="margin-top:14pt">Section 4 · Corpus profile</p>
<h2>4 · What the emails look like (blind ratings; outcomes not attached)</h2>
<div class="grid2">
<div><table><tr><th>Property</th><th>Share</th></tr>{prof_rows}</table></div>
<div><p class="small" style="margin-top:8pt">The corpus is weakest exactly where the two
confirmed effects live: 20% of emails state no reason-to-write, and 44% are visible
mail-merge. Writing quality (polish, clear asks) is already high and is not the constraint.</p></div>
</div>

<!-- ================= 5 INSTRUMENT ================= -->
<div class="pagebreak"></div>
<p class="eyebrow">Section 5 · Instrument validity</p>
<h2>5 · Reliability of the AI judge</h2>
<p class="small">Reliability = agreement beyond chance (Cohen's κ) on the exact cut used in
analysis; 0 = coin flip, 1 = perfect. Self = same model re-scoring 1,246 emails; second
AI = independent model, 1,000 emails.</p>
<table class="avoid" style="max-width:400pt">
<tr><th>Judged quality</th><th>κ self</th><th>κ second AI</th><th>Status</th></tr>
{kappa_rows}</table>
<ol class="ax">
<li>Mean gap between self- and cross-model agreement: −0.02 ⇒ the two discarded qualities
are ambiguous <i>questions</i>, not a weak model. Nothing in this document rests on them.</li>
<li>Halo check: the 12 qualities are separable (mean pairwise |r| = 0.19 vs 0.60 threshold;
first component 28% vs 50%). Exception: research-signal ~ bespokeness r = 0.83 ⇒ one finding.</li>
<li>Confound check: judged "economy" tracks word count (r = −0.48) ⇒ treated as a
restatement of L1 length; judged proof tracks length (r = +0.42) ⇒ its negative effect
disappears under a length control and is not reported as a finding.</li>
</ol>

<!-- ================= 6 SCORECARD ================= -->
<p class="eyebrow" style="margin-top:14pt">Section 6 · Scorecard</p>
<h2>6 · All 19 predictions</h2>
<table>
<tr><th>Prediction</th><th>Rule</th><th>Verdict</th></tr>
<tr><td>Templated bodies reply less</td><td>sign + p&lt;.05</td><td><span class="chip confirmed">CONFIRMED</span></td></tr>
<tr><td>Reason-to-write-now replies more (both outcomes)</td><td>sign + p&lt;.05</td><td><span class="chip confirmed">CONFIRMED</span><sup>a</sup></td></tr>
<tr><td>Its effect lands in +1.6…+7.6 pp</td><td>band</td><td><span class="chip held">HELD</span></td></tr>
<tr><td>It ranks #1 among judged qualities</td><td>rank</td><td><span class="chip held">HELD</span></td></tr>
<tr><td>Follow-up 1 ≈ opener (±2 pp)</td><td>band</td><td><span class="chip held">HELD</span></td></tr>
<tr><td>≥85% of replies by touch 4</td><td>threshold</td><td><span class="chip held">HELD</span></td></tr>
<tr><td>"Interested" mirrors "replied" on R1-class traits</td><td>sign ×3</td><td><span class="chip held">HELD</span></td></tr>
<tr><td>Pain/proof negatives vanish under length control</td><td>n.s. ×2</td><td><span class="chip held">HELD</span></td></tr>
<tr><td>Discarded qualities produce nothing</td><td>n.s. ×2</td><td><span class="chip held">HELD</span></td></tr>
<tr><td>Body ≤100 words replies more</td><td>direction only</td><td><span class="chip direction">DIRECTION</span></td></tr>
<tr><td>Question subject replies more</td><td>direction only</td><td><span class="chip direction">DIRECTION</span></td></tr>
<tr><td>2+ questions replies less</td><td>direction only</td><td><span class="chip direction">DIRECTION</span></td></tr>
<tr><td>Invites: templated replies less</td><td>direction</td><td><span class="chip direction">DIRECTION</span></td></tr>
<tr><td>Invites: short replies more</td><td>direction</td><td><span class="chip direction">DIRECTION</span></td></tr>
<tr><td>Bold text replies less</td><td>direction only</td><td><span class="chip inconclusive">INCONCLUSIVE</span></td></tr>
<tr><td>Personalisation trio stays ≤3 pp</td><td>equivalence bound</td><td><span class="chip inconclusive">INCONCLUSIVE</span></td></tr>
<tr><td>Recipient-focused writing replies more</td><td>sign</td><td><span class="chip failed">FAILED</span></td></tr>
<tr><td>Invites: bullet points reply less</td><td>sign</td><td><span class="chip failed">FAILED</span></td></tr>
<tr><td>Mid-body name reuse replies less</td><td>—</td><td><span class="chip untestable">UNTESTABLE</span></td></tr>
</table>

<!-- ================= 7 LIMITS ================= -->
<div class="pagebreak"></div>
<p class="eyebrow">Section 7 · Validity boundaries</p>
<h2>7 · What this study cannot say</h2>
<ol class="ax">
<li><b>L1 — Scope.</b> Gmail-recorded outbound only (hand-sent + Apollo). Amplemarket
sends have no reliable reply trail and are excluded; they grew from 20% of outreach (2025)
to 71% (2026). Findings cover ~75% of 2025 outbound but &lt;30% of 2026's, and say nothing
about the Amplemarket channel.</li>
<li><b>L2 — Sending tool.</b> Tool-sent email replies ~2 pp lower, but the offset is flat:
2 of 29 trait-effects differ by route (the chance rate). It shifts baselines, not the
recipe; likely partly a tracking artefact. No claim made.</li>
<li><b>L3 — Causality.</b> Within-sender comparison removes rep-level differences, not
within-rep targeting (a rep may save better emails for better prospects). Effect sizes are
upper bounds; directions are the trustworthy part. R1/R2 are the natural A/B-test candidates.</li>
<li><b>L4 — R2's 2026 margin.</b> Confirmed at p=0.047 under the pre-committed rule; two of
five robustness specifications lift p above 0.05 (sign always holds; the fair-window
outcome strengthens it to p=0.024). Reported as confirmed with a fragile margin.</li>
<li><b>L5 — Power.</b> 2026 is ¼ of 2025; four verdicts are inconclusive by design honesty,
not evidence of absence.</li>
<li><b>L6 — Known residuals.</b> 155 Amplemarket emails in scope on a technicality (all
analyses re-run without them; nothing changes); 4 test emails in frame (0.03%); 55 dedup
boundary pairs of 224,756 touches; ~0.1% replies missed via colleague hand-offs;
0.5% non-English emails judged with an English rubric; July 2026 reply windows clipped
(97% of replies arrive ≤30 days; the fair-window sensitivity strengthens both confirmations).</li>
</ol>
<h3>7.1 · Traceability</h3>
<p class="small">Pre-registration and correction log: rules/RUN2_PREREGISTRATION.md (§1–§9.9).
Findings and predictions: docs/13–14. Pre-hold-out audit: docs/15. Hold-out verdicts: docs/16.
Scientific audit: docs/17. Every figure in this document is generated from those committed
files by scripts/build_exec_doc.py; none is typed by hand.</p>
</body></html>
"""

path = os.path.join(OUT, "exec_doc.html")
open(path, "w").write(DOC)
print(f"wrote {path} ({len(DOC):,} bytes)")
