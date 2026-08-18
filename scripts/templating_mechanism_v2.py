"""Templating mechanism, second pass — what the graded why-now made testable.

docs/18 §C ran six probes with the BINARY why_now and got four dead ends. §C2 in
particular tested "the why-now works less well inside a template", found p=0.216, and the
claim was withdrawn. That test could not work: a yes/no cannot tell a specific reason from
a generic one, so both sides of the interaction looked the same.

With why_now_grade (docs/19) the test is runnable. Three blocks:

  A. TEMPLATING x REASON-SPECIFICITY. Does a specific reason pay inside a template?
  B. TEMPLATE SUB-TYPES (operator hypothesis, 2026-08-17). Templates are not one thing:
     blasting many people at one company differs from a merge sequence hitting one person
     per company. Does the split explain the penalty?
  C. THE SEAM (operator hypothesis, 2026-08-17). The reader only ever sees ONE email, so
     a reader-side mechanism MUST be in the text. Candidate: a specific fact welded onto a
     generic frame reads as bolted-on. Operationalised with `bespokeness`, the closest
     measured proxy ("could this have been sent to someone else unchanged").

EXPLORATORY. Post-holdout, on used data. Nothing here can confirm anything.

Usage: python3 templating_mechanism_v2.py
"""
import glob
import json
import os
import sys

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import whynow_grade_analysis as wg

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# An inbound-triggered opener is a follow-up to a hand raise, not cold outreach. It scores
# grade 4-5 legitimately ("you visited our website" IS a recipient-specific occasion) and
# replies well because the recipient already asked. Left in, it manufactures a template
# sub-type that looks like it beats hand-written mail. Block B is where this surfaced.
INBOUND_MARKERS = ("visited our website", "interactive demo", "requested a trial",
                   "trial request", "signed up", "requested more information",
                   "requested some more information", "your interest in our",
                   "joining our", "book a demo")


def load():
    d = wg.load(30)
    d = d[d["why_now_grade"].notna()].copy()
    d["tpl"] = d["is_template_3plus"] == True
    d["hi"] = d["why_now_grade"] >= 4
    d["besp"] = d["bespokeness"] >= 4
    d["dom"] = d["recipient"].astype(str).str.split("@").str[-1].str.lower()
    texts = {}
    for p in glob.glob(os.path.join(ROOT, "output/judge_batches_whynow/*.json")):
        for it in json.load(open(p)):
            texts[it["id"]] = it["text"].lower()
    d["inbound"] = d["email_id"].map(
        lambda i: any(k in texts.get(i, "") for k in INBOUND_MARKERS))
    return d


def cell(d, tpl, hi, col="replied"):
    s = d[(d["tpl"] == tpl) & (d["hi"] == hi)]
    return (100 * s[col].mean() if len(s) else np.nan), len(s)


def interaction(d):
    x = d.assign(y=d["replied"].astype(float), Tf=d["tpl"].astype(float),
                 Hf=d["hi"].astype(float))
    m = smf.ols("y ~ Tf*Hf + C(sender_local)", data=x).fit(
        cov_type="cluster", cov_kwds={"groups": x["sender_local"]})
    return 100 * m.params["Tf:Hf"], m.pvalues["Tf:Hf"]


def block_a(d):
    print("=" * 78)
    print("A. DOES A SPECIFIC REASON PAY INSIDE A TEMPLATE?")
    print("   (docs/18 §C2 asked this of the binary why_now: p=0.216, withdrawn)")
    print("=" * 78)
    for yr in (2025, 2026):
        y = d[d["yr"] == yr]
        print(f"\n--- {yr} (n={len(y)}) ---")
        print("                    generic reason      specific reason")
        for tpl, lab in [(False, "hand-written"), (True, "templated   ")]:
            (g, ng), (s, ns) = cell(y, tpl, False), cell(y, tpl, True)
            print(f"  {lab}      {g:5.1f}% (n={ng:>4})     {s:5.1f}% (n={ns:>4})")
        hg, _ = cell(y, False, False); hs, _ = cell(y, False, True)
        tg, _ = cell(y, True, False);  ts, _ = cell(y, True, True)
        print(f"\n  value of a specific reason:  hand {hs - hg:+.1f}pp   "
              f"templated {ts - tg:+.1f}pp")
        print(f"  templating penalty: among generic {tg - hg:+.1f}pp   "
              f"among specific {ts - hs:+.1f}pp")
        print("\n  within-sender, grade 4-5 -> replied:")
        for lab, sub in [("inside templates ", y[y["tpl"]]),
                         ("hand-written only", y[~y["tpl"]])]:
            b, se, p = wg.fe(sub, sub["hi"], "replied")
            print(f"    {lab} n={len(sub):>4}  {100 * b:+.2f}pp "
                  f"(SE {100 * se:.2f}, p={p:.4f})")
        b, p = interaction(y)
        print(f"\n  FORMAL INTERACTION: {b:+.2f}pp  p={p:.4f}")

    print("\n--- raw templating ratios, for the '2x-4x' claim ---")
    for yr in (2025, 2026):
        y = d[d["yr"] == yr]
        rt = 100 * y[y["tpl"]]["replied"].mean()
        rh = 100 * y[~y["tpl"]]["replied"].mean()
        print(f"  {yr}: templated {rt:.1f}% vs hand {rh:.1f}%  ->  {rh / rt:.1f}x")


def block_b(d):
    print("\n" + "=" * 78)
    print("B. TEMPLATE SUB-TYPES — real split, but it is an inbound confound")
    print("=" * 78)
    t = d[(d["yr"] == 2025) & d["tpl"] & d["template_hash"].notna()].copy()
    g = t.groupby("template_hash").agg(n=("email_id", "size"), ndom=("dom", "nunique"))
    g["dps"] = g["ndom"] / g["n"]
    t = t.merge(g[["dps"]], left_on="template_hash", right_index=True)
    t["kind"] = np.where(t["dps"] <= 0.34, "1 many-people-few-firms",
                np.where(t["dps"] >= 0.9, "3 one-person-per-firm", "2 mixed"))
    out = t.groupby("kind").agg(
        sends=("email_id", "size"), templates=("template_hash", "nunique"),
        mean_grade=("why_now_grade", "mean"),
        pct_specific=("hi", lambda s: 100 * s.mean()),
        pct_inbound=("inbound", lambda s: 100 * s.mean()),
        reply=("replied", lambda s: 100 * s.mean()))
    print(); print(out.round(1).to_string())
    h = d[(d["yr"] == 2025) & ~d["tpl"]]
    print(f"\n  hand-written reference   sends={len(h)}  "
          f"mean_grade={h['why_now_grade'].mean():.1f}  "
          f"pct_specific={100 * h['hi'].mean():.1f}  "
          f"reply={100 * h['replied'].mean():.1f}")
    print("\n  The one sub-type that beats hand-written is 83% specific and heavily")
    print("  inbound-triggered. Its three biggest templates, by send count:")
    per = t[t["dps"] >= 0.9]
    texts = {}
    for p in glob.glob(os.path.join(ROOT, "output/judge_batches_whynow/*.json")):
        for it in json.load(open(p)):
            texts[it["id"]] = it["text"]
    gg = per.groupby("template_hash").agg(n=("email_id", "size"),
                                          rep=("replied", "sum")).sort_values(
        "n", ascending=False)
    for h_ in gg.index[:3]:
        eid = per[per["template_hash"] == h_]["email_id"].iloc[0]
        pct = 100 * gg.loc[h_, "rep"] / gg.loc[h_, "n"]
        snippet = texts[eid][:95].replace("\n", " ")
        print(f"    n={gg.loc[h_, 'n']:>3} reply={pct:>3.0f}%  {snippet}...")


def block_c(d):
    print("\n" + "=" * 78)
    print("C. THE SEAM — a specific fact on a generic frame? REJECTED")
    print("=" * 78)
    y = d[d["yr"] == 2025]
    print("\n  bespokeness = 'could this have been sent to someone else unchanged?'")
    print("  Among emails WITH a specific reason (grade 4-5):")
    for lab, sub in [("hand-written", y[~y["tpl"] & y["hi"]]),
                     ("templated   ", y[y["tpl"] & y["hi"]])]:
        print(f"    {lab} n={len(sub):>4}  mean besp {sub['bespokeness'].mean():.2f}"
              f"  top-2-box {100 * sub['besp'].mean():5.1f}%"
              f"  reply {100 * sub['replied'].mean():5.1f}%")
    print("\n  If the seam were the mechanism, a specific reason inside a BESPOKE body")
    print("  should outperform one inside a generic body. It does not:")
    for tpl, lab in [(False, "hand-written"), (True, "templated   ")]:
        s = y[(y["tpl"] == tpl) & y["hi"]]
        a, b = s[s["besp"]], s[~s["besp"]]
        print(f"    {lab} bespoke {100 * a['replied'].mean():5.1f}% (n={len(a):>4})"
              f"   generic {100 * b['replied'].mean():5.1f}% (n={len(b):>4})")
    print("\n  The templated row runs BACKWARDS, and the cause is block B's confound:")
    s = y[y["tpl"] & y["hi"]]
    for lab, sub in [("bespoke", s[s["besp"]]), ("generic", s[~s["besp"]])]:
        print(f"    {lab} body: inbound-triggered share "
              f"{100 * sub['inbound'].mean():5.1f}%")
    print("\n  Same split, inbound-triggered removed:")
    s2 = s[~s["inbound"]]
    for lab, sub in [("bespoke", s2[s2["besp"]]), ("generic", s2[~s2["besp"]])]:
        print(f"    {lab} body: {100 * sub['replied'].mean():5.1f}% (n={len(sub):>4})")
    print("\n  And bespokeness does not absorb the interaction at all:")
    x = y.assign(y_=y["replied"].astype(float), Tf=y["tpl"].astype(float),
                 Hf=y["hi"].astype(float), Bf=y["besp"].astype(float))
    for form, lab in [("y_ ~ Tf*Hf + C(sender_local)", "raw"),
                      ("y_ ~ Tf*Hf + Bf + C(sender_local)", "+ bespokeness"),
                      ("y_ ~ Tf*Hf + Bf*Hf + C(sender_local)", "+ bespokeness x reason")]:
        m = smf.ols(form, data=x).fit(cov_type="cluster",
                                      cov_kwds={"groups": x["sender_local"]})
        print(f"    {lab:<24} interaction {100 * m.params['Tf:Hf']:+.2f}pp "
              f"p={m.pvalues['Tf:Hf']:.4f}")

    print("\n" + "=" * 78)
    print("THE CLEAN 2x2 — inbound-triggered openers removed, 2025 cold only")
    print("=" * 78)
    c = y[~y["inbound"]]
    print("\n                    generic reason      specific reason")
    for tpl, lab in [(False, "hand-written"), (True, "templated   ")]:
        (g, ng), (s, ns) = cell(c, tpl, False), cell(c, tpl, True)
        print(f"  {lab}      {g:5.1f}% (n={ng:>4})     {s:5.1f}% (n={ns:>4})")
    hg, _ = cell(c, False, False); hs, _ = cell(c, False, True)
    tg, _ = cell(c, True, False);  ts, _ = cell(c, True, True)
    print(f"\n  value of a specific reason:  hand {hs - hg:+.1f}pp   "
          f"templated {ts - tg:+.1f}pp")
    b, p = interaction(c)
    print(f"  FORMAL INTERACTION: {b:+.2f}pp  p={p:.4f}  (n={len(c)})")
    print("  Removing inbound STRENGTHENS it — the confound was working against the "
          "finding.")


if __name__ == "__main__":
    d = load()
    block_a(d)
    block_b(d)
    block_c(d)
