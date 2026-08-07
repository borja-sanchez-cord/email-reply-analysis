"""Assemble the analysis frame: one row per eligible opener with everything joined.

Applies, in this order (each step's loss is counted and printed — the waterfall
is a reportable output, not a silent filter):
  1. opener in study window (Jan 2025 - Jul 2026)
  2. opener sent from a rep mailbox (sequencer-opened pushes are unmeasurable)
  3. no eligibility exclusion (bounced / incoming within gap / reply into thread)
  4. sender is a CA (confirmed_ca or fallback_ca; see docs/06_sender_roles.md)
  5. sender-month passed the inbound-visibility check (docs: sync_check.py)
  6. opener body is not empty

Outcome columns:
  replied     = at least one candidate reply to this push was classified `human`
  interested  = that human reply's intent is one of the forward-motion intents

Usage: python3 build_frame.py [G]      (default 30)
Output: data/frame_G{G}.parquet
"""
import os
import sys

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "output")

INTERESTED_INTENTS = {"wants_call", "asks_question", "wants_materials", "referral"}


def main():
    G = int(sys.argv[1]) if len(sys.argv) > 1 else 30

    P = pd.read_parquet(os.path.join(DATA, f"pushes_G{G}.parquet"))
    roles = pd.read_csv(os.path.join(OUT, "sender_roles.csv"))
    replies = pd.read_parquet(os.path.join(DATA, "reply_labels.parquet"))
    types = pd.read_parquet(os.path.join(DATA, "type_labels.parquet"))
    feats = pd.read_parquet(os.path.join(DATA, "features_openers.parquet"))
    sync = pd.read_parquet(os.path.join(DATA, "rep_month_sync.parquet"))

    waterfall = [("all pushes", len(P))]
    P = P[P["in_study"]]
    waterfall.append(("opener in Jan2025-Jul2026", len(P)))
    P = P[P["channel"] == "mailbox"]
    waterfall.append(("opener sent from rep mailbox", len(P)))
    P = P[P["exclusions"] == ""]
    waterfall.append(("no eligibility exclusion", len(P)))

    ca = roles[roles["ca_class"].isin(["confirmed_ca", "fallback_ca"])]
    ca_map = dict(zip(ca["sender_local"], ca["ca_class"]))
    conf_map = dict(zip(roles["sender_local"], roles["confidence"]))
    P = P[P["sender_local"].isin(ca_map)]
    P["ca_class"] = P["sender_local"].map(ca_map)
    P["role_confidence"] = P["sender_local"].map(conf_map)
    waterfall.append(("sender is a CA", len(P)))

    P["month"] = P["opener_ts"].dt.to_period("M").astype(str)
    ok = set(zip(sync[sync["ok"]]["local"], sync[sync["ok"]]["month"]))
    P = P[[(l, m) in ok for l, m in zip(P["sender_local"], P["month"])]]
    waterfall.append(("sender-month has inbound visibility", len(P)))

    # outcomes from the blind reply classifier
    human = set(replies[replies["category"] == "human"]["email_id"].astype(str))
    intent = dict(zip(replies["email_id"].astype(str), replies["intent"]))

    def outcome(ids_str):
        ids = [i for i in (ids_str or "").split(",") if i]
        hits = [i for i in ids if i in human]
        if not hits:
            return False, False, len(ids), len([i for i in ids if i in intent])
        interested = any(intent.get(i) in INTERESTED_INTENTS for i in hits)
        return True, interested, len(ids), len([i for i in ids if i in intent])

    res = P["cand_reply_ids"].apply(outcome)
    P["replied"] = [r[0] for r in res]
    P["interested"] = [r[1] for r in res]
    P["n_cand_replies"] = [r[2] for r in res]
    P["n_cand_labelled"] = [r[3] for r in res]

    # types + features
    P["opener_id"] = P["opener_id"].astype(str)
    tmap = dict(zip(types["email_id"].astype(str), types["type"]))
    rmap = dict(zip(types["email_id"].astype(str), types["is_reply_like"]))
    P["type"] = P["opener_id"].map(tmap)
    P["is_reply_like"] = P["opener_id"].map(rmap)
    feats["email_id"] = feats["email_id"].astype(str)
    P = P.merge(feats, left_on="opener_id", right_on="email_id", how="left")
    P = P[~P["empty_body"].fillna(True)]
    waterfall.append(("body not empty", len(P)))

    P["year"] = P["opener_ts"].dt.year
    P.to_parquet(os.path.join(DATA, f"frame_G{G}.parquet"), index=False)

    print(f"=== eligibility waterfall (G={G}) ===")
    prev = None
    for name, n in waterfall:
        drop = "" if prev is None else f"  (-{prev - n})"
        print(f"  {name:<38} {n:>7}{drop}")
        prev = n
    print(f"\nunlabelled candidate replies (classifier gaps): "
          f"{(P['n_cand_replies'] - P['n_cand_labelled']).sum()} of {P['n_cand_replies'].sum()}")
    print(f"\nby year:\n{P.groupby('year').size().to_string()}")
    print(f"\nby type:\n{P['type'].value_counts(dropna=False).to_string()}")
    print(f"\nreply rate overall: {P['replied'].mean() * 100:.1f}%  "
          f"interested: {P['interested'].mean() * 100:.1f}%")
    print(f"\nreply rate by type & year:")
    print((P.groupby(["type", "year"])["replied"].agg(["size", "mean"])
           .assign(mean=lambda d: (d["mean"] * 100).round(1)).to_string()))


if __name__ == "__main__":
    main()
