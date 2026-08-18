"""The Apollo cut — follow-up value where the rep is not choosing per-touch.

docs/09's unfixable problem: whether a silent prospect gets touch n+1 is a rep's judgement
of that prospect, so the pooled curve mixes "the email worked" with "the rep picked well".
Apollo follow-ups are different: steps fire from a sequence template. The judgement happens
ONCE, at enrollment; touches 2..k then go out on autopilot. So among Apollo-sequenced
pushes the per-touch population is nearly unselected, and the touch-4 rate is the closest
thing to an experiment already in the data.

Validity check reported first: continuation among still-silent prospects. If Apollo pushes
really are on autopilot, their continuation should be far above the hand-sent 38-56%. If it
is not, the premise fails and the cut is worthless — say so and stop.

Per-touch tool identity: mailbox rows carry tool_flag (§9.9 twins); sequencer rows carry
source_detail. A push is APOLLO-SEQ if every follow-up touch is Apollo-fired, HAND if every
follow-up touch is a plain mailbox send. Mixed and Amplemarket pushes are excluded.

EXPLORATORY. Enrollment itself is still selected (which prospects get sequenced), so
LEVELS across classes are not comparable; the informative object is the SHAPE of the
Apollo curve — does touch 4 still land when nobody chose to send it?

Usage: python3 followup_apollo.py [--G 30]
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
                              columns=["email_id", "recipient", "ts", "channel",
                                       "source_detail"]).sort_values(["recipient", "ts"])
    tf = pd.read_parquet(os.path.join(DATA, "tool_flag.parquet"))
    tf["email_id"] = tf["email_id"].astype(str)
    touches["email_id"] = touches["email_id"].astype(str)
    touches = touches.merge(tf[["email_id", "tool"]], on="email_id", how="left")

    def touch_tool(row):
        if row["channel"] == "sequencer":
            return row["source_detail"] or "sequencer?"
        if pd.notna(row["tool"]):
            return row["tool"]              # mailbox row that a sequencer also logged
        return "hand"

    touches["ttool"] = touches.apply(touch_tool, axis=1)
    by_rcpt = {k: v for k, v in touches.groupby("recipient")}

    allp = pd.read_parquet(os.path.join(DATA, f"pushes_G{G}.parquet"),
                           columns=["recipient", "push_no", "opener_ts"]).sort_values(
        ["recipient", "push_no"])
    nxt = allp.groupby("recipient")["opener_ts"].shift(-1)
    next_by_key = dict(zip(allp["recipient"] + "|" + allp["push_no"].astype(str), nxt))

    touch_times, touch_tools = {}, {}
    for r in frame.itertuples():
        g = by_rcpt.get(r.recipient)
        if g is None:
            touch_times[r.push_key] = []
            touch_tools[r.push_key] = []
            continue
        m = g[g["ts"] >= r.opener_ts]
        nx = next_by_key.get(r.push_key)
        if pd.notna(nx):
            m = m[m["ts"] < nx]
        touch_times[r.push_key] = list(m["ts"])
        touch_tools[r.push_key] = list(m["ttool"])
    return frame, touch_times, touch_tools, reply_times


def classify(tools):
    """Class of a push by its FOLLOW-UP touches (2..). Opener route is irrelevant here."""
    fu = tools[1:]
    if not fu:
        return "no_followups"
    if all(t == "Apollo Integration" for t in fu):
        return "apollo_seq"
    if all(t == "hand" for t in fu):
        return "hand"
    return "mixed_or_am"


def curve(frame, touch_times, reply_times, keys):
    rows, at_risk = [], list(keys)
    for n in range(1, MAX_TOUCH + 1):
        sent, replied, still, stopped = [], [], [], 0
        for pk in at_risk:
            ts = touch_times.get(pk, [])
            r = reply_times.get(pk)
            if len(ts) < n:
                stopped += 1
                continue
            t_n = ts[n - 1]
            if r is not None and r <= t_n:
                continue
            sent.append(pk)
            t_next = ts[n] if len(ts) > n else None
            if r is not None and r > t_n and (t_next is None or r <= t_next):
                replied.append(pk)
            else:
                still.append(pk)
        k, m = len(replied), len(sent)
        lo, hi = wilson(k, m)
        silent_pool = m - k + stopped        # still-silent entering the next stage
        rows.append({"touch": n, "got_it": m, "replied": k,
                     "rate": round(100 * k / m, 2) if m else np.nan,
                     "lo": round(100 * lo, 1) if m else np.nan,
                     "hi": round(100 * hi, 1) if m else np.nan,
                     "rep_stopped": stopped})
        at_risk = still
    return pd.DataFrame(rows)


def continuation(touch_times, reply_times, keys):
    """Among still-silent after touch n, share that got touch n+1."""
    out = []
    for n in range(1, 6):
        cont, tot = 0, 0
        for pk in keys:
            ts = touch_times.get(pk, [])
            r = reply_times.get(pk)
            if len(ts) < n:
                continue
            t_n = ts[n - 1]
            if r is not None and r <= t_n:
                continue
            t_next = ts[n] if len(ts) > n else None
            if r is not None and r > t_n and (t_next is None or r <= t_next):
                continue                      # replied to touch n — leaves the pool
            tot += 1
            if t_next is not None:
                cont += 1
        out.append({"after_touch": n, "still_silent": tot,
                    "got_next_pct": round(100 * cont / tot, 1) if tot else np.nan})
    return pd.DataFrame(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--G", type=int, default=30)
    args = ap.parse_args()
    frame, tt, tl, rt = load(args.G)

    frame["cls"] = frame["push_key"].map(lambda k: classify(tl.get(k, [])))
    print("push classes by follow-up route:")
    print(frame["cls"].value_counts().to_string())

    for cls in ("apollo_seq", "hand"):
        keys = list(frame[frame["cls"] == cls]["push_key"])
        print("\n" + "=" * 74)
        print(f"{cls.upper()}  ({len(keys)} pushes)")
        print("=" * 74)
        print("\ncontinuation among still-silent (the validity check):")
        print(continuation(tt, rt, keys).to_string(index=False))
        print("\nconditional reply-rate curve:")
        print(curve(frame, tt, rt, keys).to_string(index=False))

    print("\nEnrollment is still selected, so compare SHAPES, not levels, across classes.")


if __name__ == "__main__":
    main()
