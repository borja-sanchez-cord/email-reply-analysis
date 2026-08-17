"""Post-holdout follow-up analyses (docs/18). Ad-hoc work, frozen as code.

Three blocks, all run on 2025 cold pitches unless stated, all reproducible:

  A. STRUCTURAL — how outreach itself changed 2025 -> 2026 (channel, volume, style).
     Outcome-blind except the reply-rate line; needs no holdout protection.
  B. SEND VOLUME — a NEW effect found after the holdout closed: each doubling of a
     rep's same-day send volume costs ~1.3pp of reply rate, independent of templating.
     NOT pre-registered. Exploratory, reported as such.
  C. TEMPLATING MECHANISM — why does templating cost 2-4x? Six probes, four dead ends.
     Recorded so nobody re-runs them.

Usage: python3 followup_analyses.py
"""
import numpy as np
import os
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
INTERNAL = {"encord.com", "encord.ai", "tryencord.com", "cord.tech"}


def load():
    f = pd.read_parquet(f"{DATA}/frame_G30.parquet")
    f["email_id"] = f["email_id"].astype(str)
    j = pd.read_parquet(f"{DATA}/judge_scores.parquet")
    j["email_id"] = j["email_id"].astype(str)
    cj = pd.read_parquet(f"{DATA}/opener_contact_join.parquet")
    cj["email_id"] = cj["email_id"].astype(str)
    d = f.merge(j, on="email_id", how="left").merge(
        cj[["email_id", "employees", "jobtitle", "industry", "seniority"]],
        on="email_id", how="left")
    return d


def fe(df, y, x, extra="", cluster="sender_local"):
    b = df.copy()
    b["_y"] = b[y].astype(float)
    b["_x"] = b[x].astype(float)
    form = f"_y ~ _x + {extra} C({cluster})" if extra else f"_y ~ _x + C({cluster})"
    m = smf.ols(form, data=b).fit(cov_type="cluster", cov_kwds={"groups": b[cluster]})
    return 100 * m.params["_x"], m.pvalues["_x"]


# ---------------------------------------------------------------- A. structural
def block_a():
    print("=" * 78)
    print("A. HOW OUTREACH CHANGED 2025 -> 2026")
    print("=" * 78)
    em = pd.read_parquet(f"{DATA}/emails_norm.parquet")
    o = em[em["direction"].isin(["EMAIL", "FORWARDED_EMAIL"]) & em["is_internal_sender"]
           & ~em["is_warmup"] & ~em["apollo_inbound"]].copy()
    t = o.explode("to_addrs").rename(columns={"to_addrs": "recipient"}).dropna(subset=["recipient"])
    t = t[~t["recipient"].str.split("@").str[-1].isin(INTERNAL)]
    t = t[t["ts"].dt.year.isin([2025, 2026])].copy()
    # dedup across routes: one row per real send (Apollo logs a Gmail twin)
    nsub = (t["subject_clean"].str.lower().str.replace(r"\s+", " ", regex=True)
            .str.strip().str.slice(0, 60))
    t["k"] = (t["from_email"] + "|" + t["recipient"] + "|" + nsub + "|"
              + t["ts"].dt.floor("2h").astype("int64").astype(str))
    tool = t[t["source"] == "INTEGRATION"].groupby("k")["source_detail"].first()
    t["tool"] = t["k"].map(tool)
    s = t.drop_duplicates("k").copy()
    s["channel"] = s["tool"].fillna("Gmail hand-sent")
    s["ym"] = s["ts"].dt.strftime("%Y-%m")
    s["year"] = s["ts"].dt.year

    x = pd.crosstab(s["year"], s["channel"]); x["TOTAL"] = x.sum(1)
    print("\nsends, each counted once:"); print(x.to_string())
    print("\nshare of all sends:")
    print((100 * x.div(x["TOTAL"], axis=0)).drop(columns="TOTAL").round(1).to_string())
    mo = {2025: 12, 2026: 7}
    print("\nper month:")
    for y in (2025, 2026):
        r = x.loc[y]
        print(f"  {y}: " + " | ".join(f"{c} {r[c]/mo[y]:,.0f}" for c in x.columns if c != "TOTAL")
              + f" | TOTAL {r['TOTAL']/mo[y]:,.0f}")
    print(f"\ntotal volume change per month: {(x.loc[2026,'TOTAL']/7)/(x.loc[2025,'TOTAL']/12):.2f}x")
    print("\nmonthly by channel (shows the Apollo -> Amplemarket switchover):")
    print(pd.crosstab(s["ym"], s["channel"]).to_string())

    d = load()
    cp = d[d["type"] == "cold_pitch"]
    print("\nstyle of cold pitches (outcome-blind):")
    rows = [("templated (3+ identical)", lambda z: z["is_template_3plus"].astype(bool)),
            ("visible mail-merge (bespokeness<=2)", lambda z: z["bespokeness"] <= 2),
            ("has a why-now", lambda z: z["why_now"] == True),
            ("question in subject", lambda z: z["subject_is_question"].astype(bool)),
            ("reuses name mid-body", lambda z: z["name_beyond_greeting"].astype(bool)),
            ("under 100 words", lambda z: z["n_words"] <= 100)]
    for name, fn in rows:
        a = 100 * fn(cp[cp.year == 2025]).mean(); b = 100 * fn(cp[cp.year == 2026]).mean()
        print(f"  {name:<38} {a:5.1f}% -> {b:5.1f}%")
    print(f"  {'median words':<38} {cp[cp.year==2025]['n_words'].median():5.0f}  -> {cp[cp.year==2026]['n_words'].median():5.0f}")
    print(f"  {'reply rate':<38} {100*cp[cp.year==2025]['replied'].mean():5.1f}% -> {100*cp[cp.year==2026]['replied'].mean():5.1f}%")


# ---------------------------------------------------------------- B. send volume
def block_b(d):
    print("\n" + "=" * 78)
    print("B. SAME-DAY SEND VOLUME — new exploratory effect, NOT pre-registered")
    print("=" * 78)
    for year in (2025, 2026):
        cp = d[(d["type"] == "cold_pitch") & (d["year"] == year)].copy()
        cp["day"] = cp["opener_ts"].dt.date
        cp["burst"] = cp.groupby(["sender_local", "day"])["email_id"].transform("size")
        cp["logb"] = np.log(cp["burst"])
        cp["T"] = cp["is_template_3plus"].astype(float)
        b = pd.cut(cp["burst"], [0, 2, 5, 10, 25, 10 ** 6],
                   labels=["1-2", "3-5", "6-10", "11-25", "26+"])
        tt = cp.groupby(b, observed=False)["replied"].agg(["size", "mean"])
        tt["reply%"] = (100 * tt["mean"]).round(1)
        print(f"\n{year} reply rate by that rep's same-day volume:")
        print(tt[["size", "reply%"]].to_string())
        bv, pv = fe(cp, "replied", "logb")
        print(f"  per doubling: {bv*np.log(2):+.2f}pp p={pv:.4f}")
        # independence from templating
        m = smf.ols("y ~ T + logb + C(sender_local)",
                    data=cp.assign(y=cp["replied"].astype(float))).fit(
            cov_type="cluster", cov_kwds={"groups": cp["sender_local"]})
        print(f"  both in one model: template {100*m.params['T']:+.2f}pp (p={m.pvalues['T']:.4f})"
              f" | volume/doubling {100*m.params['logb']*np.log(2):+.2f}pp (p={m.pvalues['logb']:.4f})")


# ------------------------------------------------------- C. templating mechanism
def block_c(d):
    print("\n" + "=" * 78)
    print("C. WHY DOES TEMPLATING COST 2-4x? six probes")
    print("=" * 78)
    cp = d[(d["type"] == "cold_pitch") & (d["year"] == 2025)].copy()
    cp["T"] = cp["is_template_3plus"].astype(float)
    T = cp["T"] == 1
    W = cp["why_now"] == True

    print("\nC1. is a why-now missing from templates?  [DEAD END]")
    print(f"  templated {100*W[T].mean():.1f}% vs hand-written {100*W[~T].mean():.1f}% — identical")

    print("\nC2. does the why-now work less well inside templates?  [DEAD END — noise]")
    b = cp.assign(y=cp["replied"].astype(float), w=W.astype(float))
    m = smf.ols("y ~ w*T + C(sender_local)", data=b).fit(
        cov_type="cluster", cov_kwds={"groups": b["sender_local"]})
    print(f"  hand-written why-now {100*m.params['w']:+.1f}pp; extra when templated "
          f"{100*m.params['w:T']:+.1f}pp p={m.pvalues['w:T']:.3f} -> not distinguishable")
    g = cp.groupby([T.map({True: "templated", False: "hand-written"}),
                    W.map({True: "why-now", False: "no why-now"})])["replied"].agg(["size", "mean"])
    g["reply%"] = (100 * g["mean"]).round(1)
    print("  2x2 (still the useful slide):"); print(g[["size", "reply%"]].to_string())

    print("\nC3. is it just worse text?  [PARTIAL — 27% explained, 73% is not the text]")
    JUDGED = ["research_signal", "value_specificity", "proof_relevance", "pain_hypothesis",
              "ask_clarity", "bespokeness", "polish", "economy", "peer_tone",
              "recipient_centricity"]
    COUNT = ["n_words", "n_questions", "n_links", "n_bullets", "n_images",
             "subject_words", "n_sentences"]
    for c in JUDGED + COUNT:
        cp[c] = cp[c].astype(float)
    cp["wn"] = W.astype(float)
    cp["bold_f"] = cp["has_bold"].astype(float)
    cp["greet_f"] = cp["greeting_has_name"].astype(float)
    b0, p0 = fe(cp, "replied", "T")
    b3, p3 = fe(cp, "replied", "T",
                " + ".join(COUNT + JUDGED) + " + wn + bold_f + greet_f + ")
    print(f"  sender FE only: {b0:+.2f}pp p={p0:.4f}")
    print(f"  + all 19 measured text features: {b3:+.2f}pp p={p3:.4f}")
    print(f"  share of penalty explained by measurable text: {100*(1-b3/b0):.0f}%")

    print("\nC4. does it scale with copies sent?  [DEAD END — flat, so it's a cliff not a slope]")
    bk = pd.cut(cp["template_repeats"], [0, 1, 2, 4, 9, 24, 10 ** 6],
                labels=["1", "2", "3-4", "5-9", "10-24", "25+"])
    tt = cp.groupby(bk, observed=False)["replied"].agg(["size", "mean"])
    tt["reply%"] = (100 * tt["mean"]).round(1)
    print(tt[["size", "reply%"]].to_string())
    tm = cp[cp["template_repeats"] >= 3].copy()
    tm["logn"] = np.log(tm["template_repeats"])
    bv, pv = fe(tm, "replied", "logn")
    print(f"  per doubling of copies: {bv*np.log(2):+.2f}pp p={pv:.4f} -> no dose-response")

    print("\nC5. spam filtering?  [WEAK EVIDENCE AGAINST — no company-size gradient]")
    cp["emp"] = pd.to_numeric(cp["employees"], errors="coerce")
    for lab, sub in [("<200 emp", cp[cp["emp"] < 200]),
                     ("200-1999", cp[(cp["emp"] >= 200) & (cp["emp"] < 2000)]),
                     ("2000+", cp[cp["emp"] >= 2000])]:
        if len(sub) < 200:
            continue
        bb, pp = fe(sub, "replied", "T")
        print(f"  {lab:<10} n={len(sub):4d} template {bb:+.2f}pp p={pp:.3f}")
    print("  (bigger firms have stronger filters; penalty barely moves -> humans, not filters)")

    print("\nC6. reply LATENCY — the one positive clue")
    r = cp[cp["replied"]].copy()
    r["lat"] = (r["cand_reply_ts"] - r["opener_ts"]).dt.total_seconds() / 86400
    print(f"  templated median {r[r['T']==1]['lat'].median():.1f}d (n={int((r['T']==1).sum())})"
          f" vs hand-written {r[r['T']==0]['lat'].median():.1f}d (n={int((r['T']==0).sum())})")
    print("  -> mail lands and is read, then deprioritised. Filtering would not slow replies.")

    print("\nC7. are some templates good and most dead?  [DEAD END — mostly chance]")
    tmx = cp[cp["template_repeats"] >= 5]
    gg = tmx.groupby("template_hash")["replied"].agg(["size", "sum"])
    gg = gg[gg["size"] >= 5]
    p = gg["sum"].sum() / gg["size"].sum()
    exp_zero = ((1 - p) ** gg["size"]).mean()
    chi = (((gg["sum"] - gg["size"] * p) ** 2) / (gg["size"] * p * (1 - p))).sum()
    print(f"  {len(gg)} templates; zero-reply observed {100*(gg['sum']==0).mean():.0f}% "
          f"vs {100*exp_zero:.0f}% expected by chance")
    print(f"  overdispersion chi2={chi:.0f} df={len(gg)-1} p={stats.chi2.sf(chi, len(gg)-1):.2e} "
          f"-> templates differ, but only {(gg['sum']/gg['size']).var()/np.mean(p*(1-p)/gg['size']):.2f}x chance")


if __name__ == "__main__":
    block_a()
    d = load()
    block_b(d)
    block_c(d)
