"""Step 5 — the check that comes before any analysis: rep-month inbound visibility.

If neither a rep's mailbox sync nor Apollo's inbox log was capturing incoming mail
in a month, every opener they sent that month shows zero replies — indistinguishable
from a rep who writes badly. Those rep-months must be dropped from Question 1.

Rule (pre-registered, adapted to the corrected data model): for each sender-identity
(local part across the four internal domains) × calendar month with any mailbox
openers, require at least one inbound email (either route) addressed to that
identity (To contains any of their four internal addresses) or sharing a thread
with their outgoing mail that month.

Output: data/rep_month_sync.parquet
"""
import os

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
DOMS = ("encord.com", "encord.ai", "tryencord.com", "cord.tech")


def main():
    inbound = pd.read_parquet(os.path.join(DATA, "inbound.parquet"))
    inbound["month"] = inbound["ts"].dt.to_period("M").astype(str)
    touches = pd.read_parquet(os.path.join(DATA, "touches.parquet"))
    touches["month"] = touches["ts"].dt.to_period("M").astype(str)
    touches["local"] = touches["from_email"].str.split("@").str[0]

    # inbound addressed to each internal local part
    it = inbound.explode("to_addrs").dropna(subset=["to_addrs"])
    it = it[it["to_addrs"].str.endswith(tuple("@" + d for d in DOMS))]
    it["local"] = it["to_addrs"].str.split("@").str[0]
    r1 = it.groupby(["local", "month"]).size().rename("n_inc_to")

    # inbound sharing a thread with the rep's outgoing that month
    thr = touches.dropna(subset=["thread_id"])[["local", "month", "thread_id"]].drop_duplicates()
    ith = inbound.dropna(subset=["thread_id"])[["thread_id", "month"]].drop_duplicates()
    j = thr.merge(ith, on="thread_id", suffixes=("", "_inb"))
    j = j[j["month"] == j["month_inb"]]
    r2 = j.groupby(["local", "month"]).size().rename("n_inc_thread")

    mb = touches[touches["channel"] == "mailbox"]
    base = (mb.groupby(["local", "month"]).size().rename("n_out_mailbox").reset_index())
    base = base.merge(r1.reset_index(), on=["local", "month"], how="left")
    base = base.merge(r2.reset_index(), on=["local", "month"], how="left")
    base[["n_inc_to", "n_inc_thread"]] = base[["n_inc_to", "n_inc_thread"]].fillna(0)
    base["n_incoming"] = base[["n_inc_to", "n_inc_thread"]].max(axis=1)
    base["ok"] = base["n_incoming"] > 0
    base.to_parquet(os.path.join(DATA, "rep_month_sync.parquet"), index=False)

    bad = base[~base["ok"]]
    print(f"rep-months with mailbox outgoing: {len(base)}; ZERO inbound: {len(bad)}")
    print(f"mailbox sends in dead rep-months: {bad['n_out_mailbox'].sum()} "
          f"of {base['n_out_mailbox'].sum()}")
    if len(bad):
        print("\ndead rep-months with most outgoing:")
        print(bad.sort_values("n_out_mailbox", ascending=False)
              [["local", "month", "n_out_mailbox"]].head(25).to_string(index=False))


if __name__ == "__main__":
    main()
