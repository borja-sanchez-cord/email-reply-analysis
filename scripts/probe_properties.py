"""Step 1a — ask HubSpot which properties exist on the email object (READ-ONLY).

Writes the full property catalogue to data/email_properties.json and prints a
compact summary so the field list can be chosen from evidence, not copied from
the old study. Also probes fill rates on a small recent sample.
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hs import load_token, get, search

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
os.makedirs(DATA, exist_ok=True)


def main():
    token = load_token()

    # 1. Sanity: token works, read-only endpoint.
    me = get("/crm/v3/objects/emails?limit=1", token)
    print(f"token OK — sample email object id: {me['results'][0]['id'] if me.get('results') else 'none'}")

    # 2. Full property catalogue for the email object.
    props = get("/crm/v3/properties/emails", token).get("results", [])
    with open(os.path.join(DATA, "email_properties.json"), "w") as f:
        json.dump(props, f, indent=1)
    print(f"\n{len(props)} properties on the email object -> data/email_properties.json")
    for p in sorted(props, key=lambda x: x["name"]):
        print(f"  {p['name']:<45} {p.get('type','?'):<12} {p.get('label','')[:60]}")

    # 3. Also catalogue contacts / companies / owners once, for later choices.
    for obj in ("contacts", "companies"):
        cat = get(f"/crm/v3/properties/{obj}", token).get("results", [])
        with open(os.path.join(DATA, f"{obj}_properties.json"), "w") as f:
            json.dump(cat, f, indent=1)
        print(f"\n{len(cat)} properties on {obj} -> data/{obj}_properties.json")


if __name__ == "__main__":
    main()
