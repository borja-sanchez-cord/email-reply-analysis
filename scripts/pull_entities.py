"""Step 1e — pull email→contact links, contacts, companies. READ-ONLY, resumable.

Runs after pull_universe.py. Stages:
  assoc     data/assoc/shard_*.json      email_id -> [contact_ids], sharded, resumable
  contacts  data/contacts.jsonl.gz       batch-read of every associated contact
  companies data/companies.jsonl.gz      batch-read of every contact's primary company

Contact/company fields chosen from the property catalogues (see
docs/01_field_choices.md); fill rates are computed on this pull and reported,
never assumed. Persona fields are pulled solely to verify the brief's claim
that they are empty, then discarded.
"""
import glob
import gzip
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hs import load_token, batch_read, batch_read_associations

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
ASSOC_DIR = os.path.join(DATA, "assoc")
os.makedirs(ASSOC_DIR, exist_ok=True)

CONTACT_PROPS = [
    "email", "firstname", "lastname", "jobtitle", "job_title___apollo",
    "seniority", "hs_seniority", "job_seniority", "country", "country___apollo",
    "industry", "company", "organisation_name", "associatedcompanyid", "createdate",
    "hubspot_owner_id", "hs_persona", "functional_persona", "ca_contact_owner_2",
]

COMPANY_PROPS = [
    "name", "domain", "numberofemployees", "employee_count", "hs_employee_range",
    "industry", "industry___apollo", "country", "vertical__aligned_by_team",
]

SHARD = 20000


def load_email_ids():
    ids = []
    for path in sorted(glob.glob(os.path.join(DATA, "universe", "month_*.jsonl.gz"))):
        with gzip.open(path, "rt") as f:
            for line in f:
                ids.append(json.loads(line)["id"])
    return list(dict.fromkeys(ids))


def stage_assoc(token, email_ids):
    shards = [email_ids[i:i + SHARD] for i in range(0, len(email_ids), SHARD)]
    for n, shard in enumerate(shards):
        path = os.path.join(ASSOC_DIR, f"shard_{n:03d}.json")
        if os.path.exists(path) and os.path.getsize(path) > 0:
            continue
        print(f"assoc shard {n + 1}/{len(shards)} ({len(shard)} emails)…", flush=True)
        result = batch_read_associations("emails", "contacts", shard, token, throttle=0.06)
        with open(path + ".tmp", "w") as f:
            json.dump(result, f)
        os.rename(path + ".tmp", path)
    # merged view
    merged = {}
    for path in sorted(glob.glob(os.path.join(ASSOC_DIR, "shard_*.json"))):
        merged.update(json.load(open(path)))
    print(f"assoc: {len(merged)} emails have >=1 contact", flush=True)
    return merged


def stage_contacts(token, assoc):
    path = os.path.join(DATA, "contacts.jsonl.gz")
    if os.path.exists(path) and os.path.getsize(path) > 0:
        print("contacts: already done", flush=True)
        return
    ids = sorted({str(c) for cs in assoc.values() for c in cs})
    print(f"contacts: {len(ids)} to fetch", flush=True)
    rows = batch_read("contacts", ids, token, CONTACT_PROPS, throttle=0.06)
    with gzip.open(path + ".tmp", "wt") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    os.rename(path + ".tmp", path)
    print(f"contacts: wrote {len(rows)}", flush=True)


def stage_companies(token):
    path = os.path.join(DATA, "companies.jsonl.gz")
    if os.path.exists(path) and os.path.getsize(path) > 0:
        print("companies: already done", flush=True)
        return
    comp_ids = set()
    with gzip.open(os.path.join(DATA, "contacts.jsonl.gz"), "rt") as f:
        for line in f:
            c = json.loads(line)
            cid = c["properties"].get("associatedcompanyid")
            if cid:
                comp_ids.add(str(cid))
    print(f"companies: {len(comp_ids)} to fetch", flush=True)
    rows = batch_read("companies", sorted(comp_ids), token, COMPANY_PROPS, throttle=0.06)
    with gzip.open(path + ".tmp", "wt") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    os.rename(path + ".tmp", path)
    print(f"companies: wrote {len(rows)}", flush=True)


if __name__ == "__main__":
    token = load_token()
    email_ids = load_email_ids()
    print(f"{len(email_ids)} emails in universe", flush=True)
    assoc = stage_assoc(token, email_ids)
    stage_contacts(token, assoc)
    stage_companies(token)
    print("ENTITIES PULL COMPLETE", flush=True)
