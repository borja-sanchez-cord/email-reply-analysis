"""Question 2 — the follow-up curve.

Of the people who didn't (humanly) reply to email 1 of a push, what share replied
after email 2? Of those still silent, after email 3? Etc. Conditional step-by-step,
which avoids the "5-email people ignored 4 emails by construction" trap.

Restricted to pushes whose opener is a mailbox send by a confirmed CA in the study
window (replies to sequencer-opened pushes are invisible — trap 1). Touches include
sequencer follow-ups; because replies to sequencer *touches* may also be invisible,
the curve is computed twice: (a) all such pushes, (b) only pushes where every touch
is a mailbox send. Differences are reported, not hidden.

Usage: python3 analyze_q2.py <pushes.parquet> <reply_labels.parquet> [--dataset 2025|2026|all]
reply_labels: email_id -> category/intent from the reply classifier.
"""
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def curve(pushes, touch_ts_by_push, human_reply_ts, max_n=8):
    """pushes: df with push_key; touch_ts sorted; human_reply_ts: push_key -> ts|None"""
    rows = []
    at_risk = list(pushes["push_key"])
    for n in range(1, max_n + 1):
        # eligible: pushes still unreplied after touch n's send AND that sent touch n
        sent_n, replied_after_n = [], []
        still = []
        for pk in at_risk:
            ts = touch_ts_by_push.get(pk, [])
            if len(ts) < n:
                continue  # never sent touch n — leaves the population (rep stopped)
            r = human_reply_ts.get(pk)
            t_n = ts[n - 1]
            if r is not None and r <= t_n:
                continue  # replied before touch n went out — not at risk for touch n
            sent_n.append(pk)
            t_next = ts[n] if len(ts) > n else None
            # reply attributed to touch n: after touch n, before touch n+1 (or any later
            # reply if touch n was the last touch)
            if r is not None and r > t_n and (t_next is None or r <= t_next):
                replied_after_n.append(pk)
            else:
                still.append(pk)
        k, m = len(replied_after_n), len(sent_n)
        lo, hi = wilson(k, m)
        rows.append({"touch": n, "at_risk_sent": m, "replied": k,
                     "rate": k / m if m else float("nan"),
                     "lo": lo, "hi": hi})
        at_risk = still
    return pd.DataFrame(rows)


def main():
    pushes_path, labels_path = sys.argv[1], sys.argv[2]
    dataset = "all"
    for a in sys.argv:
        if a.startswith("--dataset="):
            dataset = a.split("=")[1]

    P = pd.read_parquet(os.path.join(DATA, pushes_path))
    labels = pd.read_parquet(os.path.join(DATA, labels_path))
    human_ids = set(labels[labels["category"] == "human"]["email_id"].astype(str))

    emails = pd.read_parquet(os.path.join(DATA, "emails_norm.parquet"),
                             columns=["email_id", "ts"])
    ts_by_id = dict(zip(emails["email_id"].astype(str), emails["ts"]))

    touches = pd.read_parquet(os.path.join(DATA, "touches.parquet"),
                              columns=["recipient", "ts", "source", "email_id"])

    P = P[(P["in_study"]) & (P["channel"] == "mailbox") & (P["exclusions"] == "")
          & P["sender_is_ca"]].copy()
    if dataset == "2025":
        P = P[P["opener_ts"].dt.year == 2025]
    elif dataset == "2026":
        P = P[P["opener_ts"].dt.year == 2026]
    P["push_key"] = P["recipient"] + "|" + P["push_no"].astype(str)

    # first HUMAN reply ts per push
    human_reply_ts = {}
    for _, r in P.iterrows():
        best = None
        for cid in (r["cand_reply_ids"] or "").split(","):
            if cid and cid in human_ids:
                t = ts_by_id.get(cid)
                if t is not None and (best is None or t < best):
                    best = t
        human_reply_ts[r["push_key"]] = best

    # touch timestamps per push (need push_no on touches — recompute per recipient set)
    # touches were already segmented in build_pushes with the same G; rather than
    # re-segment, join on recipient and window [opener_ts, next push or +inf)
    P_sorted = P.sort_values(["recipient", "opener_ts"])
    tmap = {}
    src_map = {}
    tt = touches.sort_values(["recipient", "ts"])
    grouped = {k: v for k, v in tt.groupby("recipient")}
    nxt_start = P_sorted.groupby("recipient")["opener_ts"].shift(-1)
    for (idx, r), nstart in zip(P_sorted.iterrows(), nxt_start):
        g = grouped.get(r["recipient"])
        if g is None:
            continue
        m = g[(g["ts"] >= r["opener_ts"])]
        if pd.notna(nstart):
            m = m[m["ts"] < nstart]
        tmap[r["push_key"]] = list(m["ts"])
        src_map[r["push_key"]] = list(m["source"])

    for variant in ("all", "mailbox_only"):
        sel = P
        if variant == "mailbox_only":
            keep = [pk for pk, srcs in src_map.items() if all(s == "EMAIL" for s in srcs)]
            sel = P[P["push_key"].isin(keep)]
        c = curve(sel, tmap, human_reply_ts)
        print(f"\n=== follow-up curve [{variant}] ({dataset}; {len(sel)} pushes) ===")
        print(c.to_string(index=False,
                          formatters={"rate": "{:.3f}".format,
                                      "lo": "{:.3f}".format, "hi": "{:.3f}".format}))
        c.to_csv(os.path.join(ROOT, "output", f"q2_curve_{variant}_{dataset}.csv"), index=False)


if __name__ == "__main__":
    main()
