"""Step 2a — normalise the raw universe into three tables (no eligibility decisions).

Outputs:
  data/emails_norm.parquet   one row per email engagement, cleaned + flags
  data/touches.parquet       one row per (true outbound email × external To-recipient)
  data/inbound.parquet       one row per inbound email (both capture routes, deduped)

Semantics per docs/03_data_model_discoveries.md:
  - Internal sender domains: encord.com, encord.ai, tryencord.com, cord.tech.
  - Apollo logs inbox mail as direction=EMAIL with subject markers
    "[Apollo] [Email] [<<]" / "Email: <<"  (inbound)   and ">>" (outbound).
  - Inbound = external INCOMING_EMAIL + external Apollo-inbound, deduped on
    (from_email, normalised subject, timestamp bucket ±1h).
  - Touches = internal-sender outbound (NOT inbound-logged, NOT warmup) exploded
    to external To-recipients.
"""
import glob
import gzip
import json
import os
import re
import sys

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

WARMUP_MARKERS = ("lemwarmup", "lemwarm", "amplemarketwarmup", "warmupemail")
ADDR_RE = re.compile(r"[A-Za-z0-9._%+\-']+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
INTERNAL_DOMAINS = {"encord.com", "encord.ai", "tryencord.com", "cord.tech"}

APOLLO_IN = re.compile(r"^(\[Apollo\] \[[^\]]+\] \[<<\]|Email: <<)\s*")
APOLLO_OUT = re.compile(r"^(\[Apollo\] \[[^\]]+\] \[>>\]|Email: >>)\s*")
APOLLO_ANY = re.compile(r"^(\[Apollo\] \[[^\]]+\] \[[^\]]+\]|Email: (<<|>>))\s*")


def parse_addrs(raw):
    if not raw:
        return []
    return list(dict.fromkeys(a.lower() for a in ADDR_RE.findall(raw)))


def main():
    rows = []
    for path in sorted(glob.glob(os.path.join(DATA, "universe", "month_*.jsonl.gz"))):
        with gzip.open(path, "rt") as f:
            for line in f:
                r = json.loads(line)
                p = r["properties"]
                rows.append({
                    "email_id": r["id"],
                    "ts": p.get("hs_timestamp"),
                    "direction": p.get("hs_email_direction"),
                    "status": p.get("hs_email_status"),
                    "subject": p.get("hs_email_subject") or "",
                    "preview": p.get("hs_body_preview") or "",
                    "from_email": (p.get("hs_email_from_email") or "").lower().strip(),
                    "to_raw": p.get("hs_email_to_email") or "",
                    "to_raw2": p.get("hs_email_to_raw") or "",
                    "thread_id": p.get("hs_email_thread_id"),
                    "message_id": p.get("hs_email_message_id"),
                    "source": p.get("hs_object_source"),
                    "source_detail": p.get("hs_object_source_detail_1"),
                    "owner_id": p.get("hubspot_owner_id"),
                    "team_id": p.get("hubspot_team_id"),
                    "ooo_flag": p.get("hs_incoming_email_is_out_of_office"),
                    "bounce_msg": p.get("hs_email_bounce_error_detail_message"),
                })
    df = pd.DataFrame(rows).drop_duplicates("email_id")
    df["ts"] = pd.to_datetime(df["ts"], utc=True, format="mixed")
    subj_l = df["subject"].str.lower().str.replace(r"[\s\-_]", "", regex=True)
    df["is_warmup"] = subj_l.apply(lambda s: any(m in s for m in WARMUP_MARKERS))
    df["to_addrs"] = (df["to_raw"] + ";" + df["to_raw2"]).apply(parse_addrs)
    df["from_domain"] = df["from_email"].str.split("@").str[-1]
    df["is_internal_sender"] = df["from_domain"].isin(INTERNAL_DOMAINS)
    df["apollo_inbound"] = df["subject"].str.match(APOLLO_IN)
    df["apollo_outbound"] = df["subject"].str.match(APOLLO_OUT)
    df["subject_clean"] = df["subject"].str.replace(APOLLO_ANY, "", regex=True)

    print(f"{len(df)} emails after dedup")
    print(f"apollo_inbound={df.apollo_inbound.sum()}  apollo_outbound={df.apollo_outbound.sum()}")

    # ---- inbound table ----
    inc_a = df[(df["direction"] == "INCOMING_EMAIL") & ~df["is_internal_sender"]].copy()
    inc_a["route"] = "mailbox_sync"
    inc_b = df[(df["direction"] == "EMAIL") & df["apollo_inbound"]
               & ~df["is_internal_sender"]].copy()
    inc_b["route"] = "apollo_log"
    inbound = pd.concat([inc_a, inc_b], ignore_index=True)
    # dedup across routes: same sender, same normalised subject, same hour-bucket
    norm_subj = (inbound["subject_clean"].str.lower()
                 .str.replace(r"^(re|fwd?|aw)\s*:\s*", "", regex=True)
                 .str.replace(r"\s+", " ", regex=True).str.strip().str.slice(0, 60))
    bucket = inbound["ts"].dt.floor("2h").astype("int64")
    key = inbound["from_email"] + "|" + norm_subj + "|" + bucket.astype(str)
    inbound["dedup_key"] = key
    before = len(inbound)
    inbound = inbound.sort_values("route", ascending=False)  # keep mailbox_sync first? no:
    # prefer mailbox_sync rows (they carry thread_id); sort so mailbox_sync kept
    inbound["route_rank"] = (inbound["route"] != "mailbox_sync").astype(int)
    inbound = (inbound.sort_values(["dedup_key", "route_rank"])
               .drop_duplicates("dedup_key").drop(columns=["route_rank", "dedup_key"]))
    print(f"inbound: {before} rows -> {len(inbound)} after cross-route dedup "
          f"({(inbound['route'] == 'mailbox_sync').sum()} mailbox_sync, "
          f"{(inbound['route'] == 'apollo_log').sum()} apollo_log)")
    inbound = inbound.drop(columns=["to_raw", "to_raw2"])
    inbound.to_parquet(os.path.join(DATA, "inbound.parquet"), index=False)

    # ---- emails_norm ----
    df.drop(columns=["to_raw", "to_raw2"]).to_parquet(
        os.path.join(DATA, "emails_norm.parquet"), index=False)

    # ---- touches ----
    out_mask = (df["direction"].isin(["EMAIL", "FORWARDED_EMAIL"])
                & df["is_internal_sender"] & ~df["is_warmup"] & ~df["apollo_inbound"])
    t = df[out_mask].explode("to_addrs").rename(columns={"to_addrs": "recipient"})
    t = t.dropna(subset=["recipient"])
    t["rcpt_domain"] = t["recipient"].str.split("@").str[-1]
    t = t[~t["rcpt_domain"].isin(INTERNAL_DOMAINS)]
    # channel: how this send reached the prospect
    t["channel"] = "other"
    t.loc[t["source"] == "EMAIL", "channel"] = "mailbox"
    t.loc[(t["source"] == "INTEGRATION"), "channel"] = "sequencer"
    t = t[["email_id", "ts", "recipient", "rcpt_domain", "from_email", "owner_id",
           "source", "source_detail", "channel", "subject_clean", "thread_id",
           "status", "bounce_msg"]]
    # dedup: same send captured twice (mailbox sync + Apollo >> log)
    nsub = (t["subject_clean"].str.lower().str.replace(r"\s+", " ", regex=True)
            .str.strip().str.slice(0, 60))
    tb = t["ts"].dt.floor("2h").astype("int64")
    t["dedup_key"] = t["from_email"] + "|" + t["recipient"] + "|" + nsub + "|" + tb.astype(str)
    before = len(t)
    t["ch_rank"] = t["channel"].map({"mailbox": 0, "sequencer": 1, "other": 2})
    t = (t.sort_values(["dedup_key", "ch_rank"]).drop_duplicates("dedup_key")
         .drop(columns=["dedup_key", "ch_rank"]))
    print(f"touches: {before} -> {len(t)} after cross-route dedup")
    t = t.sort_values(["recipient", "ts"]).reset_index(drop=True)
    t.to_parquet(os.path.join(DATA, "touches.parquet"), index=False)
    print(f"distinct recipients: {t['recipient'].nunique()}")
    print(t["channel"].value_counts().to_string())


if __name__ == "__main__":
    main()
