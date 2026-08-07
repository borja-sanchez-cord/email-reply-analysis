"""Step 1d — pull all owners (active + archived) with their teams. READ-ONLY."""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hs import load_token, get

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
os.makedirs(DATA, exist_ok=True)


def main():
    token = load_token()
    owners = []
    for archived in ("false", "true"):
        after = None
        while True:
            path = f"/crm/v3/owners/?limit=100&archived={archived}"
            if after:
                path += f"&after={after}"
            resp = get(path, token)
            for o in resp.get("results", []):
                o["_archived_flag"] = archived == "true"
                owners.append(o)
            after = resp.get("paging", {}).get("next", {}).get("after")
            time.sleep(0.11)
            if not after:
                break
    with open(os.path.join(DATA, "owners.json"), "w") as f:
        json.dump(owners, f, indent=1)
    n_teams = sum(1 for o in owners if o.get("teams"))
    print(f"wrote {len(owners)} owners ({sum(o['_archived_flag'] for o in owners)} archived; "
          f"{n_teams} with teams) -> data/owners.json")


if __name__ == "__main__":
    main()
