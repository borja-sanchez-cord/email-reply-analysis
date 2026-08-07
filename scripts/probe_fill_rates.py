"""Step 1b — probe fill rates of candidate email properties on real samples.

Pulls ~600 emails from each of three months spread across the window
(2025-03, 2025-11, 2026-05), both directions, and reports what share of
records have each candidate property filled, split by direction. This is the
evidence for the final field list (trap 4: check when a field started being
filled in). READ-ONLY.
"""
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hs import load_token, search

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

CANDIDATES = [
    "hs_timestamp", "hs_createdate", "hs_email_direction", "hs_email_status",
    "hs_email_subject", "hs_body_preview", "hs_email_from_email", "hs_email_to_email",
    "hs_email_to_raw", "hs_email_cc_email", "hs_email_thread_id", "hs_email_message_id",
    "hs_in_reply_to_engagement_id", "hs_email_sent_via", "hs_object_source",
    "hs_object_source_detail_1", "hs_object_source_label", "hubspot_owner_id",
    "hubspot_team_id", "hs_incoming_email_is_out_of_office", "hs_email_bounce_error_detail_message",
    "hs_email_logged_from", "hs_sequence_id", "hs_template_id", "hs_email_headers",
    "hs_attachment_ids", "hs_email_reply_count", "hs_was_imported",
]

WINDOWS = {
    "2025-03": (1740787200000, 1743465599999),
    "2025-11": (1761955200000, 1764547199999),
    "2026-05": (1777593600000, 1780271999999),
}


def main():
    token = load_token()
    sample = {}
    for label, (lo, hi) in WINDOWS.items():
        filters = [{"propertyName": "hs_timestamp", "operator": "BETWEEN",
                    "value": str(lo), "highValue": str(hi)}]
        rows = []
        after = None
        while len(rows) < 600:
            payload = {"filterGroups": [{"filters": filters}], "properties": CANDIDATES,
                       "limit": 200,
                       "sorts": [{"propertyName": "hs_timestamp", "direction": "ASCENDING"}]}
            if after:
                payload["after"] = after
            resp = search("emails", token, payload)
            rows.extend(resp.get("results", []))
            after = resp.get("paging", {}).get("next", {}).get("after")
            if not after:
                break
        sample[label] = rows
        print(f"{label}: {len(rows)} sampled (portal total in window: {resp.get('total')})")

    with open(os.path.join(DATA, "fill_rate_sample.json"), "w") as f:
        json.dump(sample, f)

    # fill-rate table: window x direction x property
    for label, rows in sample.items():
        by_dir = defaultdict(list)
        for r in rows:
            d = r["properties"].get("hs_email_direction") or "NONE"
            by_dir[d].append(r)
        print(f"\n=== {label} ===")
        for d, rs in sorted(by_dir.items()):
            print(f"  direction={d}: n={len(rs)}")
        header = f"  {'property':<42}" + "".join(f"{d[:14]:>16}" for d in sorted(by_dir))
        print(header)
        for prop in CANDIDATES:
            cells = []
            for d in sorted(by_dir):
                rs = by_dir[d]
                filled = sum(1 for r in rs if (r["properties"].get(prop) not in (None, "")))
                cells.append(f"{100*filled/len(rs):>15.0f}%")
            print(f"  {prop:<42}" + "".join(cells))

    # distinct values for the enums that matter
    for prop in ("hs_email_direction", "hs_email_status", "hs_email_sent_via",
                 "hs_object_source", "hs_object_source_detail_1", "hs_email_logged_from",
                 "hs_incoming_email_is_out_of_office"):
        vals = defaultdict(int)
        for rows in sample.values():
            for r in rows:
                vals[str(r["properties"].get(prop))] += 1
        top = sorted(vals.items(), key=lambda x: -x[1])[:12]
        print(f"\n{prop}: " + ", ".join(f"{v}×{c}" for v, c in top))


if __name__ == "__main__":
    main()
