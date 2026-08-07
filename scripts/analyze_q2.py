"""Question 2 — how many follow-ups were needed before a reply came.

The curve: of the people who did NOT reply to email 1 of a push, what share replied
after email 2? Of those still silent, after email 3? And so on. Conditional
step-by-step, which is the honest construction: it never compares "people who got 5
emails" with "people who got 2" (that comparison measures when reps stopped, not
whether chasing works).

Population: pushes whose OPENER is a mailbox send by a CA in the study window and
that passed the same eligibility filters as Question 1 (data/frame_G30.parquet).
Follow-up touches include sequencer sends, per the brief. Because replies to
sequencer touches may be invisible, the curve is also computed on the subset whose
every touch is a mailbox send, and both are reported.

A person leaves the population when the rep stops emailing them — that is the
unfixable selection the write-up must state: the number of emails someone received
partly reflects the rep's opinion of them.

Usage: python3 analyze_q2.py [--G 30] [--year 0|2025|2026]
"""
import argparse
import os

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "output")

MAX_TOUCH = 8


def wilson(k, n, z=1.96):
    if n == 0:
        return (np.nan, np.nan)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def build_curve(frame, touch_times, reply_times):
    """frame: df with push_key. touch_times/reply_times: dict push_key -> [ts] / ts|None"""
    rows = []
    at_risk = list(frame["push_key"])
    for n in range(1, MAX_TOUCH + 1):
        sent_n, replied_n, still = [], [], []
        stopped = 0
        for pk in at_risk:
            ts = touch_times.get(pk, [])
            r = reply_times.get(pk)
            if len(ts) < n:
                stopped += 1          # rep stopped before sending touch n
                continue
            t_n = ts[n - 1]
            if r is not None and r <= t_n:
                continue              # already replied before this touch went out
            sent_n.append(pk)
            t_next = ts[n] if len(ts) > n else None
            if r is not None and r > t_n and (t_next is None or r <= t_next):
                replied_n.append(pk)
            else:
                still.append(pk)
        k, m = len(replied_n), len(sent_n)
        lo, hi = wilson(k, m)
        rows.append({"touch": n, "people_who_got_this_touch": m,
                     "replied_after_it": k,
                     "reply_rate_pct": round(100 * k / m, 2) if m else np.nan,
                     "lo_pct": round(100 * lo, 2) if m else np.nan,
                     "hi_pct": round(100 * hi, 2) if m else np.nan,
                     "left_because_rep_stopped": stopped})
        at_risk = still
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--G", type=int, default=30)
    ap.add_argument("--year", type=int, default=0)
    args = ap.parse_args()

    frame = pd.read_parquet(os.path.join(DATA, f"frame_G{args.G}.parquet"))
    if args.year:
        frame = frame[frame["year"] == args.year]
    frame = frame.copy()
    frame["push_key"] = frame["recipient"] + "|" + frame["push_no"].astype(str)

    replies = pd.read_parquet(os.path.join(DATA, "reply_labels.parquet"))
    human = set(replies[replies["category"] == "human"]["email_id"].astype(str))
    emails = pd.read_parquet(os.path.join(DATA, "emails_norm.parquet"),
                             columns=["email_id", "ts"])
    ts_by_id = dict(zip(emails["email_id"].astype(str), emails["ts"]))

    reply_times = {}
    for _, r in frame.iterrows():
        best = None
        for cid in (r["cand_reply_ids"] or "").split(","):
            if cid and cid in human:
                t = ts_by_id.get(cid)
                if t is not None and (best is None or t < best):
                    best = t
        reply_times[r["push_key"]] = best

    # touch timestamps per push: touches to that recipient from the opener until the
    # next push's opener
    touches = pd.read_parquet(os.path.join(DATA, "touches.parquet"),
                              columns=["recipient", "ts", "channel"])
    touches = touches.sort_values(["recipient", "ts"])
    by_rcpt = {k: v for k, v in touches.groupby("recipient")}

    allp = pd.read_parquet(os.path.join(DATA, f"pushes_G{args.G}.parquet"),
                           columns=["recipient", "push_no", "opener_ts"])
    allp = allp.sort_values(["recipient", "push_no"])
    next_open = allp.groupby("recipient")["opener_ts"].shift(-1)
    next_by_key = dict(zip(allp["recipient"] + "|" + allp["push_no"].astype(str), next_open))

    touch_times, touch_channels = {}, {}
    for _, r in frame.iterrows():
        g = by_rcpt.get(r["recipient"])
        if g is None:
            continue
        m = g[g["ts"] >= r["opener_ts"]]
        nx = next_by_key.get(r["push_key"])
        if pd.notna(nx):
            m = m[m["ts"] < nx]
        touch_times[r["push_key"]] = list(m["ts"])
        touch_channels[r["push_key"]] = list(m["channel"])

    for variant in ("all touches", "mailbox-only pushes"):
        sel = frame
        if variant == "mailbox-only pushes":
            keep = {pk for pk, ch in touch_channels.items()
                    if ch and all(c == "mailbox" for c in ch)}
            sel = frame[frame["push_key"].isin(keep)]
        curve = build_curve(sel, touch_times, reply_times)
        yr = args.year or "2025+2026"
        print(f"\n=== follow-up curve [{variant}] — {yr}, {len(sel)} pushes ===")
        print(curve.to_string(index=False))
        # cumulative view: share of all pushes that ever got a human reply by touch n
        total = len(sel)
        cum = curve["replied_after_it"].cumsum()
        print(f"cumulative share of all {total} pushes replied by touch n: " +
              ", ".join(f"{i + 1}:{100 * c / total:.1f}%" for i, c in enumerate(cum)))
        curve.to_csv(os.path.join(
            OUT, f"q2_curve_{variant.split()[0]}_{yr}_G{args.G}.csv"), index=False)

    # descriptive: how many touches pushes actually get
    n_touch = pd.Series({k: len(v) for k, v in touch_times.items()})
    print(f"\ntouches per push — median {n_touch.median():.0f}, "
          f"mean {n_touch.mean():.1f}, "
          f"share with only 1: {100 * (n_touch == 1).mean():.0f}%, "
          f"with 4+: {100 * (n_touch >= 4).mean():.0f}%")


if __name__ == "__main__":
    main()
