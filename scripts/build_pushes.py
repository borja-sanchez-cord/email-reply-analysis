"""Step 2c — apply the pre-registered eligibility rules to produce pushes and openers.

Usage: python3 build_pushes.py <G_days> [suffix]

Implements rules from rules/eligibility_and_analysis_rules.md:
  - A fresh push starts after >= G days with no outgoing touch (any channel) to the person.
  - The opener is the first email of the push. Its channel is recorded
    (mailbox / sequencer / other) — Question 1 uses mailbox openers only, but
    every push is kept so shares can be reported and Question 2 can use all pushes.
  - Openers are dropped (with reasons counted) if: bounced; there was any incoming
    email from that person in the G days before; or the opener's thread contains an
    earlier email (i.e. it is a reply, not a fresh contact).
  - Sender attribution: hubspot_owner_id -> owner email, else from_email. CA status
    from docs/02_ca_identification.md; behavioural fallback computed separately.
  - Reply attachment: first incoming email from the recipient (address match)
    OR in the opener's thread (thread match), after the opener, within 90 days,
    and before the next push to that person. Both match routes recorded.
    Whether the reply is a *human* reply is decided later by the reply classifier;
    this script only attaches candidate incoming emails.
  - Follow-up counting: outgoing touches to the recipient within the push
    (opener = touch 1), for Question 2.

Output: data/pushes_G{G}.parquet (one row per push) and
        data/reply_candidates_G{G}.parquet (incoming emails to classify).
"""
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

REPLY_WINDOW_DAYS = 90

CA_EMAILS = {
    "alex.leveque@encord.com", "alyssa@encord.com", "andrew@encord.com",
    "arisha@encord.com", "colin@encord.com", "constantin@encord.com",
    "diego@encord.com", "gauri@encord.com", "george.lim@encord.com",
    "hugo@encord.com", "james.golby@encord.com", "james.sweeney@encord.com",
    "james.watson@encord.com", "joe.turner@encord.com", "kamil@encord.com",
    "kat@encord.com", "katie@encord.com", "laura.zhu@encord.com", "leo@encord.com",
    "moritz@encord.com", "nick@encord.com", "nico.fernandez@encord.com",
    "ria@encord.com", "sachit@encord.com", "satchel@encord.com",
    "shivant@encord.com", "stewart@encord.com", "tom.inglis@encord.com",
    "william@encord.com", "yianni@encord.com", "yuvi@encord.com",
}
ALL_TEAMS_MEMBERS = {  # CA-team members also in a Sales team; see docs/02
    "alex.leveque@encord.com", "alyssa@encord.com", "arisha@encord.com",
    "colin@encord.com", "james.golby@encord.com", "kamil@encord.com",
    "leo@encord.com", "tom.inglis@encord.com", "william@encord.com",
    "yianni@encord.com",
}


def main():
    G = int(sys.argv[1])
    suffix = sys.argv[2] if len(sys.argv) > 2 else f"G{G}"

    owners = json.load(open(os.path.join(DATA, "owners.json")))
    owner_email = {o["id"]: (o.get("email") or "").lower() for o in owners}

    emails = pd.read_parquet(os.path.join(DATA, "emails_norm.parquet"))
    touches = pd.read_parquet(os.path.join(DATA, "touches.parquet"))
    touches = touches.sort_values(["recipient", "ts"]).reset_index(drop=True)

    # --- incoming emails indexed by sender address and by thread ---
    inc = emails[emails["direction"] == "INCOMING_EMAIL"][
        ["email_id", "ts", "from_email", "thread_id", "subject", "ooo_flag"]
    ].copy()
    inc_by_addr = {k: v[["email_id", "ts", "thread_id"]].values
                   for k, v in inc.groupby("from_email")}
    inc_by_thread = {k: v[["email_id", "ts"]].values
                     for k, v in inc.dropna(subset=["thread_id"]).groupby("thread_id")}

    # thread -> earliest email ts + direction (to detect reply-openers / prospect-started)
    th = emails.dropna(subset=["thread_id"]).sort_values("ts")
    thread_first = th.groupby("thread_id").first()[["ts", "direction"]]

    # --- segment each recipient's touches into pushes ---
    gap = touches.groupby("recipient")["ts"].diff().dt.total_seconds() / 86400.0
    touches["new_push"] = gap.isna() | (gap >= G)
    touches["push_no"] = touches.groupby("recipient")["new_push"].cumsum()

    # precompute each push's start and the next push's start (avoids per-push scans)
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

        # exclusion checks on the opener
        excl = []
        if opener["status"] == "BOUNCED" or (opener["bounce_msg"] or "") != "":
            excl.append("bounced")
        arr = inc_by_addr.get(rcpt)
        if arr is not None:
            prior = [a for a in arr if start - pd.Timedelta(days=G) <= a[1] < start]
            if prior:
                excl.append("incoming_within_gap")
        tid = opener["thread_id"]
        if tid is not None and tid in thread_first.index:
            f = thread_first.loc[tid]
            if f["ts"] < start:
                excl.append("reply_into_existing_thread"
                            if f["direction"] != "INCOMING_EMAIL" else "prospect_started")

        # reply attachment (address route + thread route)
        reply_id, reply_ts, reply_route = None, None, None
        cands = []
        if arr is not None:
            cands += [(a[0], a[1], "addr") for a in arr if start < a[1] <= reply_deadline]
        if tid is not None and tid in inc_by_thread:
            cands += [(a[0], a[1], "thread") for a in inc_by_thread[tid]
                      if start < a[1] <= reply_deadline]
        if cands:
            # same incoming email can arrive via both routes — dedup by id, keep "thread"
            best = {}
            for cid, cts, route in sorted(cands, key=lambda x: (x[1], x[2] != "thread")):
                if cid not in best:
                    best[cid] = (cid, cts, route)
            cands = sorted(best.values(), key=lambda x: x[1])
            # all candidates go to the classifier; first HUMAN one decides, later
            for cid, _, _ in cands:
                reply_cand_ids.add(cid)
            reply_id, reply_ts, reply_route = cands[0]

        # follow-up touch count + touch number preceding first candidate reply
        touch_ts = list(grp["ts"])
        touches_before_reply = None
        if reply_ts is not None:
            touches_before_reply = sum(1 for x in touch_ts if x < reply_ts)

        oe = owner_email.get(opener["owner_id"], "")
        sender = oe or opener["from_email"]
        channel = ("mailbox" if opener["source"] == "EMAIL"
                   else "sequencer" if opener["source"] == "INTEGRATION" else "other")

        pushes.append({
            "recipient": rcpt, "push_no": pno, "opener_id": opener["email_id"],
            "opener_ts": start, "in_study": start >= study_start,
            "channel": channel, "source_detail": opener["source_detail"],
            "sender": sender, "sender_is_ca": sender in CA_EMAILS,
            "sender_all_teams": sender in ALL_TEAMS_MEMBERS,
            "owner_id": opener["owner_id"], "from_email": opener["from_email"],
            "subject": opener["subject"], "thread_id": tid,
            "exclusions": ",".join(excl),
            "n_touches": len(grp),
            "cand_reply_id": reply_id, "cand_reply_ts": reply_ts,
            "cand_reply_route": reply_route,
            "touches_before_reply": touches_before_reply,
            "cand_reply_ids": ",".join(str(c[0]) for c in cands),
        })

    P = pd.DataFrame(pushes)
    P.to_parquet(os.path.join(DATA, f"pushes_{suffix}.parquet"), index=False)

    rc = inc[inc["email_id"].isin(reply_cand_ids)]
    rc.to_parquet(os.path.join(DATA, f"reply_candidates_{suffix}.parquet"), index=False)

    S = P[P["in_study"]]
    print(f"G={G}: {len(P)} pushes total; {len(S)} with opener in Jan2025–Jul2026")
    print(f"  channel of study openers: {S['channel'].value_counts().to_dict()}")
    print(f"  exclusions on study openers: "
          f"{S[S['exclusions'] != '']['exclusions'].value_counts().to_dict()}")
    print(f"  study mailbox openers, clean: "
          f"{len(S[(S['channel'] == 'mailbox') & (S['exclusions'] == '')])}")
    print(f"  ...from confirmed CAs: "
          f"{len(S[(S['channel'] == 'mailbox') & (S['exclusions'] == '') & S['sender_is_ca']])}")
    print(f"  incoming reply-candidates to classify: {len(rc)}")


if __name__ == "__main__":
    main()
