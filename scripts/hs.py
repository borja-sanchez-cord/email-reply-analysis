"""Shared HubSpot API helpers — READ-ONLY by construction.

The token is loaded at runtime from the .env file in the project root and is
never printed, logged, or written to any output file. Every function in this
module performs a GET or a search/batch-read POST (read-only semantics);
no create/update/delete endpoint exists here by design.

Adapted from the previous study's pulling machinery (hs_common.py), which the
handoff brief explicitly allows reusing.
"""
import json
import os
import time
import urllib.request
import urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(ROOT, ".env")
BASE = "https://api.hubapi.com"


def load_token():
    """Load the HubSpot private-app token from the project .env.

    Accepts any KEY=value line whose key mentions HUBSPOT or looks like a
    token key, so we don't depend on knowing the exact variable name.
    The value is returned to callers for the Authorization header only.
    """
    candidates = []
    with open(ENV_PATH) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if not val:
                continue
            score = 0
            up = key.upper()
            if "HUBSPOT" in up or up.startswith("HS_"):
                score += 2
            if "TOKEN" in up or "KEY" in up:
                score += 1
            candidates.append((score, key, val))
    if not candidates:
        raise SystemExit("no usable key found in .env")
    candidates.sort(reverse=True)
    return candidates[0][2]


def _request(method, path, token, payload=None, retries=6):
    url = BASE + path
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    })
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 429 or e.code >= 500:
                time.sleep(min(2 ** attempt, 30))
                continue
            body = e.read().decode()[:500]
            raise RuntimeError(f"HTTP {e.code} on {path}: {body}") from None
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            time.sleep(min(2 ** attempt, 30))
    raise RuntimeError(f"retries exhausted on {path}")


def get(path, token):
    return _request("GET", path, token)


def search(object_type, token, payload):
    """POST search (read-only). Caller owns pagination."""
    return _request("POST", f"/crm/v3/objects/{object_type}/search", token, payload)


def search_all(object_type, token, filters, properties, sorts=None, page_limit=200,
               max_results=None, throttle=0.11):
    """Page through a search. HubSpot caps search pagination at 10k results;
    callers needing more must window by timestamp (see pull_emails.py)."""
    out, after = [], None
    while True:
        payload = {"filterGroups": [{"filters": filters}],
                   "properties": properties, "limit": page_limit}
        if sorts:
            payload["sorts"] = sorts
        if after:
            payload["after"] = after
        resp = search(object_type, token, payload)
        out.extend(resp.get("results", []))
        paging = resp.get("paging", {}).get("next", {})
        after = paging.get("after")
        time.sleep(throttle)
        if not after or (max_results and len(out) >= max_results):
            return resp.get("total", len(out)), out


def batch_read(object_type, ids, token, properties, throttle=0.11, log_every=5000):
    """crm/v3 batch read (read-only POST). 100 ids per call."""
    out = []
    ids = [str(x) for x in dict.fromkeys(ids)]
    for i in range(0, len(ids), 100):
        chunk = ids[i:i + 100]
        resp = _request("POST", f"/crm/v3/objects/{object_type}/batch/read", token,
                        {"inputs": [{"id": x} for x in chunk], "properties": properties})
        out.extend(resp.get("results", []))
        time.sleep(throttle)
        if i and i % log_every == 0:
            print(f"    batch_read {object_type}: {i}/{len(ids)}", flush=True)
    return out


def batch_read_associations(from_type, to_type, ids, token, throttle=0.11, log_every=20000):
    """Batch association read (read-only POST). Returns {from_id: [to_ids]}."""
    result = {}
    ids = [str(x) for x in dict.fromkeys(ids)]
    for i in range(0, len(ids), 100):
        chunk = ids[i:i + 100]
        payload = {"inputs": [{"id": x} for x in chunk]}
        resp = _request("POST", f"/crm/v4/associations/{from_type}/{to_type}/batch/read",
                        token, payload)
        for row in resp.get("results", []):
            result[row["from"]["id"]] = [t["toObjectId"] for t in row.get("to", [])]
        time.sleep(throttle)
        if i and i % log_every == 0:
            print(f"    assoc {from_type}->{to_type}: {i}/{len(ids)}", flush=True)
    return result
