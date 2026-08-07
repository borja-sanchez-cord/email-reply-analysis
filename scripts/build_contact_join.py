"""Join openers to their recipient contact (for features + judge blinding).

Route 1: HubSpot email->contact associations (data/assoc/shard_*.json), picking the
associated contact whose email matches the opener's recipient; if none match by
address, the first associated contact.
Route 2 (fallback): recipient address -> contact by exact email match.

Output: data/opener_contact_join.parquet
  opener_id, recipient, contact_id, firstname, lastname, company, jobtitle,
  seniority fields, country, industry, associatedcompanyid + company fields joined.

Also prints fill rates (trap 4: report, never assume) including the persona fields
the brief called empty.
"""
import glob
import gzip
import json
import os

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")


def main():
    assoc = {}
    for path in sorted(glob.glob(os.path.join(DATA, "assoc", "shard_*.json"))):
        assoc.update(json.load(open(path)))

    contacts = {}
    by_email = {}
    with gzip.open(os.path.join(DATA, "contacts.jsonl.gz"), "rt") as f:
        for line in f:
            c = json.loads(line)
            contacts[str(c["id"])] = c["properties"]
            em = (c["properties"].get("email") or "").lower()
            if em and em not in by_email:
                by_email[em] = str(c["id"])

    companies = {}
    with gzip.open(os.path.join(DATA, "companies.jsonl.gz"), "rt") as f:
        for line in f:
            c = json.loads(line)
            companies[str(c["id"])] = c["properties"]

    pushes = pd.concat([
        pd.read_parquet(os.path.join(DATA, f"pushes_G{g}.parquet"),
                        columns=["opener_id", "recipient", "channel", "exclusions", "in_study"])
        for g in (21, 30, 45)]).drop_duplicates("opener_id")
    pushes = pushes[(pushes["in_study"]) & (pushes["channel"] == "mailbox")
                    & (pushes["exclusions"] == "")]

    rows = []
    n_assoc, n_email, n_none = 0, 0, 0
    for _, p in pushes.iterrows():
        oid, rcpt = str(p["opener_id"]), p["recipient"]
        cid = None
        cands = [str(x) for x in assoc.get(oid, [])]
        for c in cands:
            if (contacts.get(c, {}).get("email") or "").lower() == rcpt:
                cid = c
                break
        if cid is None and cands:
            cid = cands[0]
        if cid is not None:
            n_assoc += 1
        else:
            cid = by_email.get(rcpt)
            if cid is not None:
                n_email += 1
        if cid is None:
            n_none += 1
            rows.append({"email_id": oid, "recipient": rcpt, "contact_id": None})
            continue
        cp = contacts.get(cid, {})
        comp = companies.get(str(cp.get("associatedcompanyid") or ""), {})
        rows.append({
            "email_id": oid, "recipient": rcpt, "contact_id": cid,
            "firstname": cp.get("firstname"), "lastname": cp.get("lastname"),
            "company": cp.get("company") or cp.get("organisation_name") or comp.get("name"),
            "jobtitle": cp.get("jobtitle") or cp.get("job_title___apollo"),
            "seniority": cp.get("seniority"), "hs_seniority": cp.get("hs_seniority"),
            "job_seniority": cp.get("job_seniority"),
            "country": cp.get("country") or cp.get("country___apollo") or comp.get("country"),
            "industry": cp.get("industry") or comp.get("industry"),
            "hs_persona": cp.get("hs_persona"), "functional_persona": cp.get("functional_persona"),
            "company_domain": comp.get("domain"),
            "employees": comp.get("numberofemployees") or comp.get("employee_count"),
            "employee_range": comp.get("hs_employee_range"),
            "company_industry": comp.get("industry") or comp.get("industry___apollo"),
            "vertical": comp.get("vertical__aligned_by_team"),
        })
    df = pd.DataFrame(rows)
    df.to_parquet(os.path.join(DATA, "opener_contact_join.parquet"), index=False)
    print(f"{len(df)} openers: {n_assoc} via assoc, {n_email} via email match, {n_none} unmatched")
    print("\nfill rates (%):")
    for c in df.columns:
        if c in ("email_id", "recipient"):
            continue
        print(f"  {c:<22} {df[c].notna().mean() * 100:5.1f}")


if __name__ == "__main__":
    main()
