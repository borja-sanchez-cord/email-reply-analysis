"""Step 1c — pull metadata for EVERY email engagement, 1 Sep 2024 → 31 Jul 2026.

READ-ONLY. Resumable: one output file per calendar month
(data/universe/month_YYYY-MM.jsonl.gz); months whose file exists are skipped,
so an interrupted pull resumes rather than restarting.

The search endpoint caps pagination near 10k results, so each month is pulled
through a recursive window-splitter (probe the count; if > 9500, split the
window in half) — same approach as the previous study's pulling machinery,
which the brief allows reusing.
"""
import gzip
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hs import load_token, search, search_all

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(ROOT, "data", "universe")
os.makedirs(OUTDIR, exist_ok=True)

PROPS = [
    "hs_timestamp", "hs_createdate", "hs_email_direction", "hs_email_status",
    "hs_email_subject", "hs_body_preview", "hs_email_from_email", "hs_email_to_email",
    "hs_email_to_raw", "hs_email_cc_email", "hs_email_thread_id", "hs_email_message_id",
    "hs_object_source", "hs_object_source_detail_1", "hs_object_source_label",
    "hs_email_sent_via", "hs_email_logged_from", "hubspot_owner_id", "hubspot_team_id",
    "hs_incoming_email_is_out_of_office", "hs_email_bounce_error_detail_message",
]

# Calendar months, UTC. Study window per the brief: 2024-09-01 .. 2026-07-31.
MONTHS = []
for year in (2024, 2025, 2026):
    for m in range(1, 13):
        if (year, m) < (2024, 9) or (year, m) > (2026, 7):
            continue
        MONTHS.append((year, m))

import calendar
import datetime


def month_bounds_ms(year, m):
    lo = int(datetime.datetime(year, m, 1, tzinfo=datetime.timezone.utc).timestamp() * 1000)
    last = calendar.monthrange(year, m)[1]
    hi = int(datetime.datetime(year, m, last, 23, 59, 59, 999000,
                               tzinfo=datetime.timezone.utc).timestamp() * 1000) + 999
    return lo, hi


def window(token, lo, hi, out, depth=0):
    filters = [{"propertyName": "hs_timestamp", "operator": "BETWEEN",
                "value": str(lo), "highValue": str(hi)}]
    probe = search("emails", token, {"filterGroups": [{"filters": filters}],
                                     "properties": ["hs_object_id"], "limit": 1})
    total = probe.get("total", 0)
    time.sleep(0.08)
    if total == 0:
        return
    if total > 9500 and lo < hi:
        mid = (lo + hi) // 2
        window(token, lo, mid, out, depth + 1)
        window(token, mid + 1, hi, out, depth + 1)
        return
    _, rows = search_all("emails", token, filters, PROPS, throttle=0.08,
                         sorts=[{"propertyName": "hs_timestamp", "direction": "ASCENDING"}])
    out.extend(rows)
    print(f"    window {total} rows (depth {depth}) — running {len(out)}", flush=True)


def main():
    token = load_token()
    for year, m in MONTHS:
        name = f"month_{year}-{m:02d}.jsonl.gz"
        path = os.path.join(OUTDIR, name)
        if os.path.exists(path) and os.path.getsize(path) > 0:
            print(f"{name}: already done, skipping", flush=True)
            continue
        lo, hi = month_bounds_ms(year, m)
        print(f"{name}: pulling…", flush=True)
        out = []
        window(token, lo, hi, out)
        # dedup within month by object id (recursive windows never overlap, but be safe)
        seen, rows = set(), []
        for r in out:
            if r["id"] in seen:
                continue
            seen.add(r["id"])
            rows.append(r)
        with gzip.open(path + ".tmp", "wt") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
        os.rename(path + ".tmp", path)
        print(f"{name}: wrote {len(rows)} rows", flush=True)
    print("UNIVERSE PULL COMPLETE", flush=True)


if __name__ == "__main__":
    main()
