"""Build packs for the intent/Interested accuracy check (RUN2_PREREGISTRATION §1b).

`replied` was validated at 99.0% two-pass agreement (docs/08). `interested` was only
spot-checked, and §1b promotes it to co-primary — so it needs the same standard.

Design mirrors the pass-A/pass-B logic that worked for `replied`: pass B asks a
DIFFERENT QUESTION rather than re-asking for the same label, so the two passes have
different failure modes. Pass A asked "assign one of 9 intents". Pass B asks what the
writer wants to happen next and whether a concrete next step now exists for the sender,
and the Interested label is derived mechanically afterwards in scripts/intent_accuracy.py.

Two samples, reported separately:
  primary   300 random replies that pass A called `human`  -> the §1b gate number
            (corpus-representative, so the agreement rate is an unbiased estimate)
  booster   up to 50 each of referral / wants_materials / asks_question, drawn from
            the remainder -> per-intent detail only. The three thin Interested cells
            would otherwise get ~10, ~12 and ~30 draws in a random 300, which is too
            few to characterise WHERE any disagreement sits.

The booster is never pooled into the gate number.

Usage: python3 build_intent_accuracy_batches.py
Output: output/intent_accuracy/pack_*.json  +  sample_manifest.json
"""
import glob
import json
import os

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "output")
OUTDIR = os.path.join(OUT, "intent_accuracy")

SEED = 20260814          # fixed and recorded, per §5.7
N_PRIMARY = 300
BOOSTER_INTENTS = ["referral", "wants_materials", "asks_question"]
N_BOOSTER_EACH = 50
PACK = 75


def main():
    os.makedirs(OUTDIR, exist_ok=True)

    labels = pd.read_parquet(os.path.join(DATA, "reply_labels.parquet"))
    labels["email_id"] = labels["email_id"].astype(str)
    human = labels[labels["category"] == "human"].copy()
    print(f"pass-A human replies available: {len(human)}")

    # the exact blinded text pass A saw — never re-derived from the raw bodies
    texts = {}
    for p in glob.glob(os.path.join(OUT, "reply_batches", "batch_*.json")):
        for x in json.load(open(p)):
            texts[str(x["id"])] = x
    human = human[human["email_id"].isin(texts)]
    print(f"  ...with blinded text on disk: {len(human)}")

    primary = human.sample(n=N_PRIMARY, random_state=SEED)
    rest = human[~human["email_id"].isin(set(primary["email_id"]))]

    booster_parts = []
    for it in BOOSTER_INTENTS:
        pool = rest[rest["intent"] == it]
        take = min(N_BOOSTER_EACH, len(pool))
        booster_parts.append(pool.sample(n=take, random_state=SEED))
        print(f"  booster {it}: {take} of {len(pool)} available")
    booster = pd.concat(booster_parts) if booster_parts else human.iloc[:0]

    manifest = {
        "seed": SEED,
        "primary_ids": sorted(primary["email_id"]),
        "booster_ids": sorted(booster["email_id"]),
        "primary_intent_counts": primary["intent"].value_counts().to_dict(),
        "booster_intent_counts": booster["intent"].value_counts().to_dict(),
        "note": "primary = the §1b gate sample; booster = per-intent detail only, never pooled",
    }
    json.dump(manifest, open(os.path.join(OUTDIR, "sample_manifest.json"), "w"), indent=1)

    # packs carry text only — no pass-A label, no outcome, no sender, no date
    items = [{"id": i, "subject": texts[i].get("subject", ""), "text": texts[i].get("text", "")}
             for i in sorted(set(primary["email_id"]) | set(booster["email_id"]))]
    n = 0
    for k in range(0, len(items), PACK):
        with open(os.path.join(OUTDIR, f"pack_{k // PACK}.json"), "w") as f:
            json.dump(items[k:k + PACK], f, indent=0)
        n += 1

    print(f"\n{len(items)} replies ({len(primary)} primary + {len(booster)} booster) "
          f"-> {n} packs in output/intent_accuracy/")
    print(f"seed={SEED} recorded in sample_manifest.json")
    print("\nprimary sample intent mix (pass A):")
    print(primary["intent"].value_counts().to_string())


if __name__ == "__main__":
    main()
