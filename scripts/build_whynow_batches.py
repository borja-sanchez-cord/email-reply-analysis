"""Build batches for the graded why-now pass (rules/judge_rubric.md addendum).

Design decision that removes an entire class of risk: **the item texts are not rebuilt.**
They are copied byte-for-byte out of `output/judge_batches/`, which passed the blinding
gate at 0 leaks across 12,462 items (§9.7). Re-deriving redaction here would mean a second
implementation of the thing that leaked in run 1 — the mistake `check_blinding.py`'s
docstring already records. So this script only *selects* and *regroups*.

Population: cold pitches in frame G30, both years — the population the binary `why_now`
finding was estimated on. Event invites are excluded per the addendum: an invitation's
occasion is the event, so the scale cannot vary.

Outputs:
  output/judge_batches_whynow/batch_NNNN.json           main pass
  output/judge_batches_whynow_rescore/batch_NNNN.json   10% subset, regrouped, for kappa

Usage: python3 build_whynow_batches.py
"""
import glob
import json
import os
import random

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "output", "judge_batches")
OUT = os.path.join(ROOT, "output", "judge_batches_whynow")
OUT_RS = os.path.join(ROOT, "output", "judge_batches_whynow_rescore")

BATCH = 40           # the proven size; 12-dim batches of 40 dropped items 3 times in 312
RESCORE_N = 640      # 10% of the population, 16 clean batches
SEED = 20260817      # pre-declared in the rubric addendum


def load_source():
    """Every item ever built for the judge, keyed by id, with its text untouched."""
    by_id = {}
    for p in sorted(glob.glob(os.path.join(SRC, "*.json"))):
        for it in json.load(open(p)):
            assert it["id"] not in by_id, f"duplicate id in source batches: {it['id']}"
            by_id[it["id"]] = it
    return by_id


def target_ids():
    f = pd.read_parquet(os.path.join(ROOT, "data", "frame_G30.parquet"))
    cp = f[f["type"] == "cold_pitch"]
    ids = sorted(set(cp["email_id"].astype(str)))
    years = pd.to_datetime(cp["opener_ts"]).dt.year.value_counts().sort_index()
    print(f"cold-pitch frame rows {len(cp)}, unique openers {len(ids)}")
    print("  rows by year: " + ", ".join(f"{y}={n}" for y, n in years.items()))
    return ids


def write(items, outdir, label):
    if os.path.isdir(outdir):
        for p in glob.glob(os.path.join(outdir, "*.json")):
            os.remove(p)
    os.makedirs(outdir, exist_ok=True)
    n = 0
    for i in range(0, len(items), BATCH):
        chunk = items[i:i + BATCH]
        tag = str(i // BATCH).zfill(4)
        with open(os.path.join(outdir, f"batch_{tag}.json"), "w") as fh:
            json.dump(chunk, fh, ensure_ascii=False, indent=0)
        n += 1
    print(f"{label}: {len(items)} items -> {n} batches in {os.path.relpath(outdir, ROOT)}")
    return n


def verify_verbatim(src, outdirs):
    """The whole safety argument of this script, checked rather than asserted in prose."""
    seen, bad = set(), 0
    for d in outdirs:
        for p in sorted(glob.glob(os.path.join(d, "*.json"))):
            for it in json.load(open(p)):
                s = src[it["id"]]
                if (it["subject"], it["text"]) != (s["subject"], s["text"]):
                    bad += 1
                if d == outdirs[0]:
                    seen.add(it["id"])
    assert bad == 0, f"{bad} items differ from the gate-verified source text"
    print(f"verbatim check: PASS — {len(seen)} main-pass items byte-identical to source")
    return seen


def main():
    src = load_source()
    print(f"source items available: {len(src)}")
    ids = target_ids()

    missing = [i for i in ids if i not in src]
    assert not missing, f"{len(missing)} cold-pitch ids were never judged: {missing[:5]}"

    items = [src[i] for i in ids]
    n_main = write(items, OUT, "main")

    rng = random.Random(SEED)
    sub = rng.sample(items, RESCORE_N)
    rng.shuffle(sub)   # regrouped, so run 2 never sees run 1's batch context
    n_rs = write(sub, OUT_RS, "rescore")

    kept = verify_verbatim(src, [OUT, OUT_RS])
    assert kept == set(ids), "main pass does not cover exactly the target population"
    print(f"\nagents to run: {n_main} main + {n_rs} rescore = {n_main + n_rs}")


if __name__ == "__main__":
    main()
