"""The §1b gate: is `interested` accurate enough to be a co-primary outcome?

`replied` was validated at 99.0% (docs/08). `interested` was only spot-checked, so
RUN2_PREREGISTRATION §1b requires the same standard before any Layer-2 analysis uses it:

    a 300-reply independent differently-worded second pass, measuring per-intent and
    Interested-level agreement. If Interested-level agreement is below 90%, the intent
    classifier is revised and re-measured.

Pass A (production) asked "assign one of 9 intents". Pass B never sees that list: it is
asked what the writer wants to happen next and whether a concrete next step now exists.
The Interested label is derived from pass B's answer HERE, mechanically, so the mapping
is auditable and fixed rather than negotiated by an agent mid-classification.

Reported:
  1. Interested-level agreement on the 300-reply primary sample  <- THE GATE
  2. the same excluding `referral` (the §1 sensitivity)
  3. a secondary derivation from pass B's `next_step` boolean alone
  4. per-intent agreement (primary + booster, booster never pooled into the gate)
  5. every disagreement printed with its text, so the direction can be characterised
     rather than just counted — this is what made docs/08 convincing

Usage: python3 intent_accuracy.py
"""
import glob
import json
import os

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "output")
DIR = os.path.join(OUT, "intent_accuracy")

GATE = 0.90

# Pre-registered Interested set (rules/reply_classifier_protocol.md, §1)
A_INTERESTED = {"wants_call", "asks_question", "wants_materials", "referral"}

# Pass B's forward-motion categories -> does this reply carry forward motion?
B_INTERESTED = {
    "proposes_or_accepts_meeting": True,
    "asks_for_information": True,
    "requests_document_or_demo": True,
    "redirects_to_colleague": True,
    "defers_to_later": False,
    "declines": False,
    "asks_who_are_you": False,
    "acknowledges_only": False,
    "none_of_these": False,
    "cannot_tell": None,
}

# For per-intent detail only: the nearest pass-A intent for each pass-B category.
B_TO_A = {
    "proposes_or_accepts_meeting": "wants_call",
    "asks_for_information": "asks_question",
    "requests_document_or_demo": "wants_materials",
    "redirects_to_colleague": "referral",
    "defers_to_later": "not_now",
    "declines": "not_interested",
    "asks_who_are_you": "who_is_this",
    "acknowledges_only": "other_human",
    "none_of_these": "other_human",
}


def pct(x):
    return f"{100 * x:.1f}%"


def report(d, name):
    """Interested-level agreement on a subset."""
    ok = (d["a_interested"] == d["b_interested"])
    print(f"  {name:<44} {pct(ok.mean())}  ({int(ok.sum())}/{len(d)})")
    return ok.mean()


def main():
    man = json.load(open(os.path.join(DIR, "sample_manifest.json")))
    primary_ids, booster_ids = set(man["primary_ids"]), set(man["booster_ids"])
    print(f"sample seed: {man['seed']}   primary={len(primary_ids)} booster={len(booster_ids)}")

    second = {}
    for p in sorted(glob.glob(os.path.join(DIR, "second_pass_*.json"))):
        for r in json.load(open(p)):
            second[str(r["id"])] = r
    print(f"pass-B records loaded: {len(second)}")

    labels = pd.read_parquet(os.path.join(DATA, "reply_labels.parquet"))
    labels["email_id"] = labels["email_id"].astype(str)
    amap = {r["email_id"]: r for _, r in labels.iterrows()}

    texts = {}
    for p in glob.glob(os.path.join(OUT, "reply_batches", "batch_*.json")):
        for x in json.load(open(p)):
            texts[str(x["id"])] = x

    rows = []
    for i, b in second.items():
        a = amap.get(i)
        if a is None:
            continue
        rows.append({
            "id": i,
            "sample": "primary" if i in primary_ids else ("booster" if i in booster_ids else "?"),
            "a_intent": a["intent"],
            "a_interested": a["intent"] in A_INTERESTED,
            "b_motion": b.get("motion"),
            "b_interested": B_INTERESTED.get(b.get("motion")),
            "b_next_step": b.get("next_step"),
            "b_wants": b.get("wants", ""),
        })
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(DIR, "intent_agreement.csv"), index=False)

    miss = (primary_ids | booster_ids) - set(df["id"])
    if miss:
        print(f"!! {len(miss)} sampled replies have no pass-B record — coverage gap, "
              f"list: {sorted(miss)[:20]}")

    print(f"\n{'=' * 70}")
    print("=== THE GATE: Interested-level agreement, primary sample ===")
    prim = df[(df["sample"] == "primary") & (df["b_interested"].notna())]
    cannot = int((df[df["sample"] == "primary"]["b_interested"].isna()).sum())
    print(f"  primary replies scored by both passes: {len(prim)}  "
          f"(pass-B 'cannot_tell' excluded: {cannot})")
    gate = report(prim, "Interested (pre-registered definition)")

    no_ref = prim[prim["a_intent"] != "referral"]
    report(no_ref, "Interested excluding referral (§1 sensitivity)")

    sec = prim[prim["b_next_step"].notna()]
    if len(sec):
        ok = (sec["a_interested"] == sec["b_next_step"].astype(bool))
        print(f"  {'secondary: pass-B next_step boolean alone':<44} "
              f"{pct(ok.mean())}  ({int(ok.sum())}/{len(sec)})")

    print(f"\n  base rates — pass A: {pct(prim['a_interested'].mean())} interested, "
          f"pass B: {pct(prim['b_interested'].mean())} interested")

    print(f"\n{'=' * 70}")
    print(f"VERDICT: {pct(gate)} vs gate {pct(GATE)} -> "
          f"{'PASS — interested may be used as co-primary' if gate >= GATE else 'FAIL — revise the intent classifier and re-measure before any Layer-2 analysis'}")

    print(f"\n{'=' * 70}")
    print("=== per-intent agreement (primary + booster; booster is detail only) ===")
    allr = df[df["b_interested"].notna()].copy()
    allr["b_as_a"] = allr["b_motion"].map(B_TO_A)
    t = allr.groupby("a_intent").apply(
        lambda g: pd.Series({
            "n": len(g),
            "same_interested_side": f"{pct((g['a_interested'] == g['b_interested']).mean())}",
            "exact_intent_match": f"{pct((g['a_intent'] == g['b_as_a']).mean())}",
        }), include_groups=False)
    print(t.to_string())

    print("\ncross-tab (rows = pass A intent, cols = pass B motion):")
    print(pd.crosstab(allr["a_intent"], allr["b_motion"]).to_string())

    dis = prim[prim["a_interested"] != prim["b_interested"]]
    print(f"\n{'=' * 70}")
    print(f"=== ALL {len(dis)} DISAGREEMENTS IN THE PRIMARY SAMPLE (read these) ===")
    for _, r in dis.iterrows():
        t = texts.get(r["id"], {})
        print("-" * 88)
        print(f"A={r['a_intent']} (interested={r['a_interested']})   "
              f"B={r['b_motion']} (interested={r['b_interested']})")
        print(f"  subject: {(t.get('subject') or '')[:90]}")
        print(f"  text:    {(t.get('text') or '')[:240].replace(chr(10), ' | ')}")
        print(f"  B wants: {str(r['b_wants'])[:200]}")

    json.dump({"gate": GATE, "interested_agreement": round(float(gate), 4),
               "n_primary_scored": int(len(prim)), "passed": bool(gate >= GATE),
               "seed": man["seed"]},
              open(os.path.join(DIR, "gate_result.json"), "w"), indent=1)
    print(f"\nwrote {DIR}/intent_agreement.csv and gate_result.json")


if __name__ == "__main__":
    main()
