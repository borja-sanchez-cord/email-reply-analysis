"""Does a 4th+ email actually work, or does the curve just reflect who reps chose to chase?

docs/09 built the conditional curve and correctly refused to answer this: the people who
received a 4th email are the ones a rep decided were worth a 4th email. The rate at touch 4
therefore mixes "the email worked" with "the rep picked well".

This script attacks the selection three ways instead of giving up on it.

  A. HOW SELECTIVE IS THE STOP DECISION AT ALL? Per stage, what share of still-silent
     prospects get the next touch. If reps continued with everybody the curve would already
     be causal; if they continue with 30% it is heavily selected.

  B. THE NEAR-UNSELECTED SUBSET — the main test. Reps differ in persistence, and persistence
     is closer to a habit than a per-account judgement. For a rep who continues with almost
     every silent prospect, the 4th-touch population is almost unselected, so their touch-4
     rate is close to what a 4th email does for an ordinary prospect. If it matches the
     pooled 4.2%, selection is not what produces that number.

  C. REP-LEVEL POLICY. Do persistent reps end up with more replies per prospect than
     early-stopping reps? This is the question a manager actually faces — it compares
     policies, not prospects. Confounded by rep quality, so craft markers are shown
     alongside rather than claimed as controls.

EXPLORATORY. Q2 was pre-registered as descriptive only; none of this was predicted.

Usage: python3 followup_persistence.py [--G 30]
"""
import argparse
import os

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
MAX_TOUCH = 8


def wilson(k, n, z=1.96):
    if n == 0:
        return (np.nan, np.nan)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def load(G):
    frame = pd.read_parquet(os.path.join(DATA, f"frame_G{G}.parquet")).copy()
    frame["push_key"] = frame["recipient"] + "|" + frame["push_no"].astype(str)
    replies = pd.read_parquet(os.path.join(DATA, "reply_labels.parquet"))
    human = set(replies[replies["category"] == "human"]["email_id"].astype(str))
    emails = pd.read_parquet(os.path.join(DATA, "emails_norm.parquet"),
                             columns=["email_id", "ts"])
    ts_by_id = dict(zip(emails["email_id"].astype(str), emails["ts"]))

    reply_times = {}
    for r in frame.itertuples():
        best = None
        for cid in (r.cand_reply_ids or "").split(","):
            if cid and cid in human:
                t = ts_by_id.get(cid)
                if t is not None and (best is None or t < best):
                    best = t
        reply_times[r.push_key] = best

    touches = pd.read_parquet(os.path.join(DATA, "touches.parquet"),
                              columns=["recipient", "ts", "channel"]).sort_values(
        ["recipient", "ts"])
    by_rcpt = {k: v for k, v in touches.groupby("recipient")}
    allp = pd.read_parquet(os.path.join(DATA, f"pushes_G{G}.parquet"),
                           columns=["recipient", "push_no", "opener_ts"]).sort_values(
        ["recipient", "push_no"])
    nxt = allp.groupby("recipient")["opener_ts"].shift(-1)
    next_by_key = dict(zip(allp["recipient"] + "|" + allp["push_no"].astype(str), nxt))

    touch_times = {}
    for r in frame.itertuples():
        g = by_rcpt.get(r.recipient)
        if g is None:
            touch_times[r.push_key] = []
            continue
        m = g[g["ts"] >= r.opener_ts]
        nx = next_by_key.get(r.push_key)
        if pd.notna(nx):
            m = m[m["ts"] < nx]
        touch_times[r.push_key] = list(m["ts"])
    return frame, touch_times, reply_times


def stage_records(frame, touch_times, reply_times):
    """One row per (push, stage): was this prospect still silent, did they get touch n+1,
    and did they reply to it. This is the unit the whole question lives on."""
    rows = []
    for r in frame.itertuples():
        ts = touch_times.get(r.push_key, [])
        rep = reply_times.get(r.push_key)
        for n in range(1, MAX_TOUCH + 1):
            if len(ts) < n:
                break                       # never got touch n at all
            t_n = ts[n - 1]
            if rep is not None and rep <= t_n:
                break                       # replied before touch n went out
            t_next = ts[n] if len(ts) > n else None
            replied_here = (rep is not None and rep > t_n
                            and (t_next is None or rep <= t_next))
            rows.append({"push_key": r.push_key, "sender": r.sender_local, "touch": n,
                         "replied_to_this": bool(replied_here),
                         "got_next": t_next is not None,
                         "still_silent_after": not replied_here})
    return pd.DataFrame(rows)


def block_a(sr):
    print("=" * 78)
    print("A. HOW SELECTIVE IS THE DECISION TO KEEP GOING?")
    print("=" * 78)
    print("\n  Of prospects still silent after touch n, what share got touch n+1:")
    for n in range(1, 6):
        s = sr[(sr["touch"] == n) & sr["still_silent_after"]]
        if not len(s):
            continue
        print(f"    after touch {n}: {100 * s['got_next'].mean():5.1f}% continued "
              f"({int(s['got_next'].sum()):>5} of {len(s):>5})")
    print("\n  Reps drop most silent prospects at every stage, so the pooled curve IS")
    print("  selected. That is the problem block B works around.")


def block_b(sr):
    print("\n" + "=" * 78)
    print("B. THE NEAR-UNSELECTED TEST — reps who chase almost everyone")
    print("=" * 78)
    # A rep's persistence at a stage = share of their silent prospects they continue with.
    for stage in (3, 4):
        s = sr[(sr["touch"] == stage) & sr["still_silent_after"]]
        per = s.groupby("sender")["got_next"].agg(["mean", "size"])
        per = per[per["size"] >= 30]
        if not len(per):
            continue
        print(f"\n  --- the {stage + 1}th email ---")
        print(f"  {len(per)} reps with >=30 silent prospects after touch {stage}. "
              f"Their continuation rates:")
        print(f"    min {100 * per['mean'].min():.0f}%  median "
              f"{100 * per['mean'].median():.0f}%  max {100 * per['mean'].max():.0f}%")
        # outcome at the NEXT touch, split by how selective the sending rep is
        nxt = sr[(sr["touch"] == stage + 1)].merge(
            per.rename(columns={"mean": "persistence"})[["persistence"]],
            left_on="sender", right_index=True, how="inner")
        if not len(nxt):
            continue
        bands = [(0.0, 0.35, "selective  (<35% continued)"),
                 (0.35, 0.65, "middling   (35-65%)"),
                 (0.65, 1.01, "chases nearly everyone (>65%)")]
        print(f"\n  Reply rate to touch {stage + 1}, by how selective that rep is:")
        for lo, hi, lab in bands:
            b = nxt[(nxt["persistence"] >= lo) & (nxt["persistence"] < hi)]
            if not len(b):
                print(f"    {lab:<32} — no reps in band")
                continue
            k, m = int(b["replied_to_this"].sum()), len(b)
            wlo, whi = wilson(k, m)
            print(f"    {lab:<32} {100 * k / m:5.1f}%  ({k}/{m})  "
                  f"95% CI {100 * wlo:.1f}-{100 * whi:.1f}%")
        print("\n  If the high-persistence band holds up, a 4th/5th email works for an")
        print("  ordinary silent prospect, not just for a hand-picked one.")


def block_c(sr, frame):
    print("\n" + "=" * 78)
    print("C. REP-LEVEL POLICY — do persistent reps get more replies per prospect?")
    print("=" * 78)
    first = sr[sr["touch"] == 1]
    tot = first.groupby("sender")["push_key"].nunique().rename("prospects")
    rep_any = sr.groupby(["sender", "push_key"])["replied_to_this"].max().reset_index()
    got = rep_any.groupby("sender")["replied_to_this"].sum().rename("replied")
    # persistence: mean touches per prospect, and share of prospects reaching 4+
    depth = sr.groupby(["sender", "push_key"])["touch"].max().reset_index()
    mean_depth = depth.groupby("sender")["touch"].mean().rename("mean_touches")
    deep = depth.assign(d4=depth["touch"] >= 4).groupby("sender")["d4"].mean().rename(
        "share_reaching_4")
    t = pd.concat([tot, got, mean_depth, deep], axis=1).dropna()
    t = t[t["prospects"] >= 100]
    t["reply_rate"] = 100 * t["replied"] / t["prospects"]
    t = t.sort_values("share_reaching_4")
    print(f"\n  {len(t)} reps with >=100 prospects, sorted by persistence:\n")
    print("    rep persistence (share reaching email 4+) | mean touches | reply rate | n")
    for s, r in t.iterrows():
        print(f"      {100 * r['share_reaching_4']:5.1f}%                              "
              f"  {r['mean_touches']:4.1f}        {r['reply_rate']:5.1f}%    "
              f"{int(r['prospects']):>5}")
    c1 = t["share_reaching_4"].corr(t["reply_rate"])
    c2 = t["mean_touches"].corr(t["reply_rate"])
    print(f"\n  corr(share reaching email 4+, overall reply rate) = {c1:+.3f}")
    print(f"  corr(mean touches per prospect, overall reply rate) = {c2:+.3f}")
    print("\n  Confounded by rep quality in an unknown direction: a persistent rep may be")
    print("  more diligent (biases up) or a spray-and-pray rep (biases down). Read the")
    print("  sign, not the size.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--G", type=int, default=30)
    args = ap.parse_args()
    frame, tt, rt = load(args.G)
    sr = stage_records(frame, tt, rt)
    print(f"stage records: {len(sr)} across {sr['push_key'].nunique()} pushes, "
          f"{sr['sender'].nunique()} reps\n")
    block_a(sr)
    block_b(sr)
    block_c(sr, frame)


if __name__ == "__main__":
    main()
