"""Step 5 — the check that comes before any analysis: rep-month mailbox sync.

If a rep's mailbox wasn't syncing in a month, every mailbox email they sent that
month shows zero replies — indistinguishable from a rep who writes badly.

Rule (pre-registered): for each sender × calendar month, check whether ANY
incoming email is attached anywhere in their mail that month. "Attached to
their mail" = an incoming engagement whose To-addresses include the sender's
address, OR that shares a thread_id with any of the sender's outgoing mailbox
emails that month. Rep-months with zero such incoming are dropped from
Question 1, and the number of openers removed is reported.

Output: data/rep_month_sync.parquet (sender, month, n_out_mailbox, n_incoming, ok)
"""
import os

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")


def main():
    emails = pd.read_parquet(os.path.join(DATA, "emails_norm.parquet"))
    emails["month"] = emails["ts"].dt.to_period("M").astype(str)

    out = emails[(emails["direction"] == "EMAIL") & (emails["source"] == "EMAIL")
                 & emails["is_internal_sender"]]
    inc = emails[emails["direction"] == "INCOMING_EMAIL"].copy()

    # route 1: incoming whose To includes the rep
    inc_to = inc.explode("to_addrs").rename(columns={"to_addrs": "rep"})
    r1 = inc_to.groupby(["rep", "month"]).size().rename("n_inc_to")

    # route 2: incoming sharing a thread with the rep's outgoing that month
    thr = out.dropna(subset=["thread_id"])[["from_email", "month", "thread_id"]]
    inc_thr = inc.dropna(subset=["thread_id"])[["thread_id", "month"]]
    j = thr.merge(inc_thr, on="thread_id", suffixes=("", "_inc"))
    r2 = j.groupby(["from_email", "month"]).size().rename("n_inc_thread")

    base = out.groupby(["from_email", "month"]).size().rename("n_out_mailbox").reset_index()
    base = base.rename(columns={"from_email": "rep"})
    base = base.merge(r1.reset_index(), on=["rep", "month"], how="left")
    base = base.merge(r2.reset_index().rename(columns={"from_email": "rep"}),
                      on=["rep", "month"], how="left")
    base[["n_inc_to", "n_inc_thread"]] = base[["n_inc_to", "n_inc_thread"]].fillna(0)
    base["n_incoming"] = base[["n_inc_to", "n_inc_thread"]].max(axis=1)
    base["ok"] = base["n_incoming"] > 0
    base.to_parquet(os.path.join(DATA, "rep_month_sync.parquet"), index=False)

    bad = base[~base["ok"]]
    print(f"rep-months with mailbox outgoing: {len(base)}; with ZERO incoming: {len(bad)}")
    print(f"mailbox emails in dead rep-months: {bad['n_out_mailbox'].sum()} "
          f"of {base['n_out_mailbox'].sum()}")
    print("\nworst offenders (dead rep-months with most outgoing):")
    print(bad.sort_values("n_out_mailbox", ascending=False)
          [["rep", "month", "n_out_mailbox"]].head(20).to_string(index=False))


if __name__ == "__main__":
    main()
