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
import re
import sys

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

REPLY_WINDOW_DAYS = 90

# --- addr-route subject verification (RUN2_PREREGISTRATION §9.6) -------------------
#
# The addr fallback ("any inbound from the recipient within the window") exists because
# sequencer-era emails carry no thread_id. Unchecked, it grabbed unrelated conversations:
# on heavily-touched contacts, 73% of addr-route replies had a subject that did not match
# the opener ("Intro Alec & Ross" credited with a reply titled "job in sf"). Thread-route
# matches were 100% subject-consistent, so only the addr route is gated.
#
# Rule: an addr-route candidate is kept only if its normalised subject matches the
# normalised subject of ANY outgoing touch in the push (not just the opener — a reply to
# follow-up #3 is still a reply to the push). Match = equality, or containment when the
# shorter side is >= 6 chars. Reply prefixes (Re:/Fwd:/Automatic reply:/Accepted:, DE/FR
# variants) are stripped first; remaining text is lowercased alphanumeric tokens, so
# "encord & tempo" matches "[Encord <> Tempo] Labelling and Fine-Tune".
#
# Direction of error: conservative. A genuine reply that opens a brand-new subject line is
# now dropped (counted and reported as cand_dropped_subject). That undercounts replied;
# the alternative overcounted it with other conversations, which is worse for a study
# whose outcome is "did THIS email get a reply".

SUBJECT_PREFIX_RE = re.compile(
    r"^\s*(\[[^\]]{0,30}\]\s*)?"
    r"((re|fw|fwd|aw|sv|antw|wg|automatic reply|auto[- ]?reply|autoreply|"
    r"out of office|ooo|accepted|declined|tentative|invitation|"
    r"automatische antwort|abwesenheitsnotiz|r[ée]ponse automatique)\s*:\s*)+", re.I)


def norm_subject(s):
    s = str(s or "").strip()
    prev = None
    while prev != s:
        prev = s
        s = SUBJECT_PREFIX_RE.sub("", s).strip()
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def subjects_match(reply_subject, touch_subjects):
    """True if the reply's subject ties it to any outgoing touch in the push."""
    r = norm_subject(reply_subject)
    if not r:
        return False
    for t in touch_subjects:
        t = norm_subject(t)
        if not t:
            continue
        if r == t:
            return True
        if len(min(r, t, key=len)) >= 6 and (r in t or t in r):
            return True
    return False

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
    inb_subject = dict(zip(inbound["email_id"], inbound["subject_clean"]))
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
    addr_audit = []   # §9.6: production's own record of every addr-route keep/drop
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
        dropped_subject = 0
        if arr is not None:
            touch_subjects = [s for s in grp["subject_clean"] if isinstance(s, str) and s]
            for a in arr:
                if not (start < a[1] <= reply_deadline):
                    continue
                # §9.6: addr-route candidates must be tied to the push by subject
                kept = subjects_match(inb_subject.get(a[0]), touch_subjects)
                addr_audit.append({"opener_id": opener["email_id"], "cid": a[0],
                                   "reply_subject": inb_subject.get(a[0]),
                                   "opener_subject": opener["subject_clean"],
                                   "n_touches": len(grp), "kept": kept})
                if kept:
                    cands.append((a[0], a[1], "addr"))
                else:
                    dropped_subject += 1
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
            "cand_dropped_subject": dropped_subject,
        })

    P = pd.DataFrame(pushes)
    P.to_parquet(os.path.join(DATA, f"pushes_{suffix}.parquet"), index=False)

    rc = inbound[inbound["email_id"].isin(reply_cand_ids)]
    rc.to_parquet(os.path.join(DATA, f"reply_candidates_{suffix}.parquet"), index=False)
    pd.DataFrame(addr_audit).to_parquet(
        os.path.join(DATA, f"addr_audit_{suffix}.parquet"), index=False)

    S = P[P["in_study"]]
    print(f"G={G}: {len(P)} pushes; {len(S)} openers in Jan2025–Jul2026")
    print(f"  channel: {S['channel'].value_counts().to_dict()}")
    print(f"  exclusions: {S[S['exclusions'] != '']['exclusions'].value_counts().to_dict()}")
    clean_mb = S[(S["channel"] == "mailbox") & (S["exclusions"] == "")]
    print(f"  clean mailbox openers: {len(clean_mb)}  (CA: {clean_mb['sender_is_ca'].sum()})")
    print(f"  reply candidates to classify: {len(rc)}")
    print(f"  addr-route candidates dropped by subject check (§9.6): "
          f"{int(S['cand_dropped_subject'].sum())} across {int((S['cand_dropped_subject'] > 0).sum())} pushes")


if __name__ == "__main__":
    main()
