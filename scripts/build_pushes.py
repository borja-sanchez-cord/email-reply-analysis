"""Step 2c — apply the pre-registered eligibility rules to produce pushes and openers.

Usage: python3 build_pushes.py <G_days>

Implements rules from rules/eligibility_and_analysis_rules.md over the corrected
timeline (docs/03_data_model_discoveries.md):
  - A fresh push starts after >= G days with no outgoing touch (any channel) to the person.
  - The opener is the first email of the push; channel recorded (mailbox/sequencer/other).
  - Openers dropped (reasons counted) if: bounced; incoming from that person within the
    G days before; opener's thread contains an earlier email (it's a reply, not fresh).
  - Sender identity: hubspot_owner_id -> owner email; else from_email; local part
    resolved across the four internal domains for CA matching.
  - Reply attachment: inbound (both routes) from the recipient's address OR in the
    opener's thread, after the opener, within 90 days, before the next push. The
    classifier later decides which candidates are human.
  - Follow-up counts for Question 2.

Output: data/pushes_G{G}.parquet, data/reply_candidates_G{G}.parquet
"""
import json
import os
import sys

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

REPLY_WINDOW_DAYS = 90

CA_LOCALPARTS = {
    "alex.leveque", "alyssa", "andrew", "arisha", "colin", "constantin", "diego",
    "gauri", "george.lim", "hugo", "james.golby", "james.sweeney", "james.watson",
    "joe.turner", "kamil", "kat", "katie", "laura.zhu", "leo", "moritz", "nick",
    "nico.fernandez", "ria", "sachit", "satchel", "shivant", "stewart", "tom.inglis",
    "william", "yianni", "yuvi",
}
ALL_TEAMS_LOCALPARTS = {
    "alex.leveque", "alyssa", "arisha", "colin", "james.golby", "kamil", "leo",
    "tom.inglis", "william", "yianni",
}


def main():
    G = int(sys.argv[1])
    suffix = f"G{G}"

    owners = json.load(open(os.path.join(DATA, "owners.json")))
    owner_email = {o["id"]: (o.get("email") or "").lower() for o in owners}

    touches = pd.read_parquet(os.path.join(DATA, "touches.parquet"))
    touches = touches.sort_values(["recipient", "ts"]).reset_index(drop=True)
    inbound = pd.read_parquet(os.path.join(DATA, "inbound.parquet"))
    emails = pd.read_parquet(os.path.join(DATA, "emails_norm.parquet"),
                             columns=["email_id", "ts", "direction", "thread_id"])

    inb_by_addr = {k: list(zip(v["email_id"], v["ts"]))
                   for k, v in inbound.groupby("from_email")}
    inb_by_thread = {k: list(zip(v["email_id"], v["ts"]))
                     for k, v in inbound.dropna(subset=["thread_id"]).groupby("thread_id")}

    th = emails.dropna(subset=["thread_id"]).sort_values("ts")
    thread_first = th.groupby("thread_id").first()[["ts", "direction"]]

    gap = touches.groupby("recipient")["ts"].diff().dt.total_seconds() / 86400.0
    touches["new_push"] = gap.isna() | (gap >= G)
    touches["push_no"] = touches.groupby("recipient")["new_push"].cumsum()

    push_start = touches.groupby(["recipient", "push_no"])["ts"].first()
    next_start = push_start.groupby(level=0).shift(-1)

    pushes = []
    reply_cand_ids = set()
    study_start = pd.Timestamp("2025-01-01", tz="UTC")

    for (rcpt, pno), grp in touches.groupby(["recipient", "push_no"], sort=False):
        opener = grp.iloc[0]
        start = opener["ts"]
        end_next = next_start.get((rcpt, pno))
        if pd.isna(end_next):
            end_next = None
        reply_deadline = start + pd.Timedelta(days=REPLY_WINDOW_DAYS)
        if end_next is not None:
            reply_deadline = min(reply_deadline, end_next)

        excl = []
        if opener["status"] == "BOUNCED" or (opener["bounce_msg"] or "") != "":
            excl.append("bounced")
        arr = inb_by_addr.get(rcpt)
        if arr is not None:
            if any(start - pd.Timedelta(days=G) <= a[1] < start for a in arr):
                excl.append("incoming_within_gap")
        tid = opener["thread_id"]
        if tid is not None and tid in thread_first.index:
            f = thread_first.loc[tid]
            if f["ts"] < start:
                excl.append("prospect_started" if f["direction"] == "INCOMING_EMAIL"
                            else "reply_into_existing_thread")

        cands = []
        if arr is not None:
            cands += [(a[0], a[1], "addr") for a in arr if start < a[1] <= reply_deadline]
        if tid is not None and tid in inb_by_thread:
            cands += [(a[0], a[1], "thread") for a in inb_by_thread[tid]
                      if start < a[1] <= reply_deadline]
        reply_id, reply_ts, reply_route = None, None, None
        if cands:
            best = {}
            for cid, cts, route in sorted(cands, key=lambda x: (x[1], x[2] != "thread")):
                if cid not in best:
                    best[cid] = (cid, cts, route)
            cands = sorted(best.values(), key=lambda x: x[1])
            for cid, _, _ in cands:
                reply_cand_ids.add(cid)
            reply_id, reply_ts, reply_route = cands[0]

        touch_ts = list(grp["ts"])
        touches_before_reply = (sum(1 for x in touch_ts if x < reply_ts)
                                if reply_ts is not None else None)

        oe = owner_email.get(opener["owner_id"], "")
        sender = oe or opener["from_email"]
        local = sender.split("@")[0]

        pushes.append({
            "recipient": rcpt, "push_no": int(pno), "opener_id": opener["email_id"],
            "opener_ts": start, "in_study": start >= study_start,
            "channel": opener["channel"], "source_detail": opener["source_detail"],
            "sender": sender, "sender_local": local,
            "sender_is_ca": local in CA_LOCALPARTS,
            "sender_all_teams": local in ALL_TEAMS_LOCALPARTS,
            "owner_id": opener["owner_id"], "from_email": opener["from_email"],
            "subject": opener["subject_clean"], "thread_id": tid,
            "exclusions": ",".join(excl),
            "n_touches": len(grp),
            "touch_channels": ",".join(grp["channel"]),
            "cand_reply_id": reply_id, "cand_reply_ts": reply_ts,
            "cand_reply_route": reply_route,
            "touches_before_reply": touches_before_reply,
            "cand_reply_ids": ",".join(str(c[0]) for c in cands) if cands else "",
        })

    P = pd.DataFrame(pushes)
    P.to_parquet(os.path.join(DATA, f"pushes_{suffix}.parquet"), index=False)

    rc = inbound[inbound["email_id"].isin(reply_cand_ids)]
    rc.to_parquet(os.path.join(DATA, f"reply_candidates_{suffix}.parquet"), index=False)

    S = P[P["in_study"]]
    print(f"G={G}: {len(P)} pushes; {len(S)} openers in Jan2025–Jul2026")
    print(f"  channel: {S['channel'].value_counts().to_dict()}")
    print(f"  exclusions: {S[S['exclusions'] != '']['exclusions'].value_counts().to_dict()}")
    clean_mb = S[(S["channel"] == "mailbox") & (S["exclusions"] == "")]
    print(f"  clean mailbox openers: {len(clean_mb)}  (CA: {clean_mb['sender_is_ca'].sum()})")
    print(f"  reply candidates to classify: {len(rc)}")


if __name__ == "__main__":
    main()
