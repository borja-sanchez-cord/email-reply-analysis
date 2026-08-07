"""Step 2a — normalise the raw universe into two tables (no eligibility decisions here).

Outputs:
  data/emails_norm.parquet   one row per email engagement, cleaned fields
  data/touches.parquet       one row per (outgoing email × external To-recipient)

Decisions made here (mechanical, documented):
  - The "to" field is semicolon-separated and may contain display names
    ("Jane Smith <jane@co.com>; bob@x.io") — parsed with a real address extractor.
  - Internal domains are found from evidence: domains that appear as *senders* of
    outgoing mail at scale. Printed for review, then hard-coded after inspection.
  - Warm-up traffic flagged by subject markers (from the reused pulling machinery).
  - Nothing is dropped except exact-duplicate engagement ids; all flags are columns,
    so every later filter is explicit and auditable.
"""
import glob
import gzip
import json
import os
import re
import sys
from collections import Counter

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

WARMUP_MARKERS = ("lemwarmup", "lemwarm", "amplemarketwarmup", "warmupemail")

ADDR_RE = re.compile(r"[A-Za-z0-9._%+\-']+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")

# Set after inspecting sender-domain distribution (printed by this script).
INTERNAL_DOMAINS = {"encord.com", "cord.tech"}


def parse_addrs(raw):
    """Extract lowercase addresses from a semicolon-separated field with display names."""
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
                    "cc_raw": p.get("hs_email_cc_email") or "",
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

    print(f"{len(df)} emails after dedup")
    print("\ndirection counts:")
    print(df["direction"].value_counts(dropna=False).to_string())
    print("\nsource counts:")
    print(df.groupby(["source", "source_detail"], dropna=False).size().to_string())
    print("\ntop 25 outgoing sender domains:")
    out_mask = df["direction"].isin(["EMAIL", "FORWARDED_EMAIL"])
    print(df.loc[out_mask, "from_domain"].value_counts().head(25).to_string())
    print(f"\nwarmup-flagged: {df['is_warmup'].sum()}")
    print(f"outgoing rows with zero parsed recipients: "
          f"{(out_mask & (df['to_addrs'].str.len() == 0)).sum()}")

    df["is_internal_sender"] = df["from_domain"].isin(INTERNAL_DOMAINS)
    dfx = df.drop(columns=["to_raw", "to_raw2"])
    dfx.to_parquet(os.path.join(DATA, "emails_norm.parquet"), index=False)

    # touches: outgoing email × external To-recipient
    t = df[out_mask & df["is_internal_sender"] & ~df["is_warmup"]].explode("to_addrs")
    t = t.rename(columns={"to_addrs": "recipient"}).dropna(subset=["recipient"])
    t["rcpt_domain"] = t["recipient"].str.split("@").str[-1]
    t = t[~t["rcpt_domain"].isin(INTERNAL_DOMAINS)]
    t = t[["email_id", "ts", "recipient", "rcpt_domain", "from_email", "owner_id",
           "source", "source_detail", "subject", "thread_id", "status", "bounce_msg"]]
    t.to_parquet(os.path.join(DATA, "touches.parquet"), index=False)
    print(f"\ntouches (outgoing, internal sender, external To-recipient, non-warmup): {len(t)}")
    print(f"distinct recipients: {t['recipient'].nunique()}")


if __name__ == "__main__":
    main()
