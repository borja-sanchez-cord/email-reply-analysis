"""Pre-registered accuracy check on the reply classifier (rules/reply_classifier_protocol.md).

300 random replies were labelled twice:
  pass A — the production classifier ("category/intent" taxonomy)
  pass B — a differently worded pass: "describe what this email is and what kind of
           process produced it", with the label DERIVED from the description here.

Different question, different failure modes. This script derives pass-B labels
mechanically from pass B's `producer` field, reports agreement on the outcome
that matters (Replied = human), and describes the direction of disagreements
with the actual text so the errors can be characterised, not just counted.
"""
import glob
import json
import os

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "output")

# pass-B producer -> is this a human writing?
PRODUCER_IS_HUMAN = {
    "person_typing": True,
    "autoresponder": False,
    "mail_server": False,
    "ticketing_system": False,
    "calendar_or_scheduling_tool": False,
    "subscription_system": False,
    "security_gateway": False,
    "marketing_system": False,
    "cannot_tell": None,
}


def main():
    second = {r["id"]: r for r in json.load(
        open(os.path.join(OUT, "reply_accuracy", "second_pass.json")))}
    main_labels = {}
    for p in glob.glob(os.path.join(OUT, "reply_labels", "batch_*.json")):
        for x in json.load(open(p)):
            main_labels[str(x["id"])] = x
    texts = {}
    for p in glob.glob(os.path.join(OUT, "reply_batches", "batch_*.json")):
        for x in json.load(open(p)):
            if x["id"] in second:
                texts[x["id"]] = x

    rows = []
    for i, b in second.items():
        a = main_labels.get(str(i))
        if not a:
            continue
        a_human = a["category"] == "human"
        b_human = PRODUCER_IS_HUMAN.get(b["producer"])
        rows.append({"id": i, "a_category": a["category"], "a_intent": a.get("intent"),
                     "a_human": a_human, "b_producer": b["producer"], "b_human": b_human,
                     "b_desc": b["description"], "b_wants": b["writer_wants"]})
    df = pd.DataFrame(rows)
    print(f"replies labelled by both passes: {len(df)} of 300 sampled")

    d = df[df["b_human"].notna()]
    agree = (d["a_human"] == d["b_human"]).mean()
    print(f"\nAGREEMENT ON 'Replied' (human vs not): {agree * 100:.1f}%  "
          f"({int((d['a_human'] == d['b_human']).sum())}/{len(d)})")
    print(f"  pass A says human: {d['a_human'].mean() * 100:.1f}%   "
          f"pass B says human: {d['b_human'].mean() * 100:.1f}%")
    print(f"  'cannot_tell' in pass B (excluded above): {(df['b_human'].isna()).sum()}")

    print("\ncross-tab (rows = pass A category, cols = pass B producer):")
    print(pd.crosstab(df["a_category"], df["b_producer"]).to_string())

    dis = d[d["a_human"] != d["b_human"]]
    print(f"\n=== ALL {len(dis)} DISAGREEMENTS (direction + evidence) ===")
    for _, r in dis.iterrows():
        t = texts.get(r["id"], {})
        print("-" * 88)
        print(f"A={r['a_category']}/{r['a_intent']}   B={r['b_producer']}")
        print(f"  subject: {(t.get('subject') or '')[:90]}")
        print(f"  text:    {(t.get('text') or '')[:220].replace(chr(10), ' | ')}")
        print(f"  B says:  {r['b_desc'][:220]}")

    df.to_csv(os.path.join(OUT, "reply_accuracy", "agreement.csv"), index=False)

    # intent-level sanity: does pass B's free-text "wants" agree with Interested?
    INTERESTED = {"wants_call", "asks_question", "wants_materials", "referral"}
    hh = df[(df["a_human"]) & (df["b_human"] == True)].copy()
    hh["a_interested"] = hh["a_intent"].isin(INTERESTED)
    print(f"\namong replies both passes call human (n={len(hh)}): "
          f"pass A marks {hh['a_interested'].mean() * 100:.0f}% as Interested")
    print("sample of pass-B 'what the writer wants' for A-Interested replies:")
    for _, r in hh[hh["a_interested"]].head(8).iterrows():
        print(f"  [{r['a_intent']:<16}] {r['b_wants'][:110]}")
    print("sample of pass-B 'what the writer wants' for A-not-Interested replies:")
    for _, r in hh[~hh["a_interested"]].head(8).iterrows():
        print(f"  [{r['a_intent']:<16}] {r['b_wants'][:110]}")


if __name__ == "__main__":
    main()
