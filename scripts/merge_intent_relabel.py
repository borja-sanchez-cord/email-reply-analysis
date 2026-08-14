"""Merge the §1b intent relabel into reply_labels.parquet.

RUN2_PREREGISTRATION §1b failed at 83.3%. `docs/11_intent_accuracy_gate.md` diagnosed the
entire gap as the undefined `other_human` catch-all. `rules/reply_classifier_protocol.md`
(addendum) wrote the boundary down as five operator rulings. This script applies the
relabel produced under those rulings.

Scope, deliberately narrow:
  - ONLY replies whose pass-A intent was `other_human`.
  - ONLY those attached to a push in the G30/G21/G45 frames — the replies that can
    actually change an outcome. Non-frame `other_human` replies keep their pass-A label;
    they feed nothing.
  - The `category` layer (human vs bot vs calendar) is NOT touched. It was validated at
    99.0% (docs/08) and has no defect.

Direction check: a 240-reply reverse sample (seed 99) of ALREADY-interested replies was
re-read blind under the same rulings. 97.5% stayed interested; 2.5% moved out. Against
62.3% moving in on the forward pass, that is a 25:1 asymmetry — evidence the relabel is a
correction, not a generous model drifting in one direction. The reverse sample is a
VALIDATION and is not applied: applying a re-read of 240 of 1,359 interested replies would
leave that bucket inconsistently labelled, which is the defect this whole exercise exists
to remove.

The original label is preserved in `intent_passA` so every change stays auditable.

Usage: python3 merge_intent_relabel.py
"""
import glob
import json
import os

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "output")

INTERESTED = {"wants_call", "asks_question", "wants_materials", "referral"}
LEGAL = INTERESTED | {"not_now", "not_interested", "unsubscribe_request",
                      "who_is_this", "other_human", "n/a"}


def load_relabel():
    """Relabelled intents, from the study-linked pass and the 5-batch model test."""
    out = {}
    for d in ("intent_relabel_frame_labels", "intent_relabel_sonnet"):
        for p in sorted(glob.glob(os.path.join(OUT, d, "batch_*.json"))):
            for x in json.load(open(p)):
                out.setdefault(str(x["id"]), x)
    return out


def main():
    lab = pd.read_parquet(os.path.join(DATA, "reply_labels.parquet"))
    lab["email_id"] = lab["email_id"].astype(str)
    n0 = len(lab)

    # replies that can actually change an outcome
    linked = set()
    for G in (30, 21, 45):
        fr = pd.read_parquet(os.path.join(DATA, f"frame_G{G}.parquet"))
        for s in fr["cand_reply_ids"].fillna(""):
            linked.update(i for i in str(s).split(",") if i)

    new = load_relabel()
    assert all(v["intent"] in LEGAL for v in new.values()), "illegal intent in relabel"

    if "intent_passA" not in lab.columns:
        lab["intent_passA"] = lab["intent"]

    eligible = (lab["category"] == "human") & (lab["intent_passA"] == "other_human") \
        & (lab["email_id"].isin(linked)) & (lab["email_id"].isin(new))
    print(f"reply labels: {n0}")
    print(f"  human & pass-A other_human & study-linked & relabelled: {int(eligible.sum())}")

    changed = 0
    for idx in lab.index[eligible]:
        i = lab.at[idx, "email_id"]
        v = new[i]["intent"]
        if v != lab.at[idx, "intent"]:
            lab.at[idx, "intent"] = v
            changed += 1
    print(f"  intents changed: {changed}")

    # invariants — §5.5
    assert len(lab) == n0, "row count changed"
    assert lab["email_id"].is_unique, "duplicate email_id"
    assert lab["intent"].isin(LEGAL).all(), "illegal intent after merge"
    assert (lab["category"] == "human").sum() == (
        pd.read_parquet(os.path.join(DATA, "reply_labels.parquet"))["category"] == "human").sum(), \
        "category layer was modified — it must not be"

    lab.to_parquet(os.path.join(DATA, "reply_labels.parquet"), index=False)

    print("\n=== intent distribution: pass A -> after relabel ===")
    h = lab[lab["category"] == "human"]
    cmp = pd.DataFrame({"pass_A": h["intent_passA"].value_counts(),
                        "after": h["intent"].value_counts()}).fillna(0).astype(int)
    cmp["change"] = cmp["after"] - cmp["pass_A"]
    print(cmp.to_string())
    print(f"\ninterested replies: {h['intent_passA'].isin(INTERESTED).sum()} -> "
          f"{h['intent'].isin(INTERESTED).sum()}")


if __name__ == "__main__":
    main()
