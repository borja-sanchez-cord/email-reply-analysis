"""Step 2b — find the fresh-push gap G from the data (pre-registered procedure).

For every recipient: time gaps between consecutive outgoing touches to them
(all channels — mailbox + sequencer — since both close a gap from the
prospect's point of view). Print the distribution at day resolution, locate
the trough between the bump/sequence cluster and the new-push spread.

Output: output/gap_distribution.csv + printed histogram + candidate troughs.
No opener selection happens here; this only fixes G.
"""
import os

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "output")
os.makedirs(OUT, exist_ok=True)


def main():
    t = pd.read_parquet(os.path.join(DATA, "touches.parquet"),
                        columns=["recipient", "ts"])
    t = t.sort_values(["recipient", "ts"])
    gaps = t.groupby("recipient")["ts"].diff().dropna()
    gd = gaps.dt.total_seconds() / 86400.0
    # collapse same-moment duplicates (same email to same person logged twice)
    gd = gd[gd > 0.001]
    print(f"{len(gd)} gaps across {t['recipient'].nunique()} recipients")

    days = np.floor(gd).astype(int).clip(upper=120)
    hist = days.value_counts().sort_index()
    hist.to_csv(os.path.join(OUT, "gap_distribution.csv"), header=["count"])

    total = len(gd)
    print("\ngap histogram (day floor, capped at 120; bar = share of all gaps):")
    for d in range(0, 91):
        c = int(hist.get(d, 0))
        bar = "#" * int(round(1000 * c / total))
        print(f"  {d:>3}d {c:>7} {bar}")
    print(f"  >90d {int(hist[hist.index > 90].sum()):>7}")

    # smoothed trough search between day 3 and day 60
    counts = np.array([hist.get(d, 0) for d in range(0, 121)], dtype=float)
    smooth = np.convolve(counts, np.ones(7) / 7, mode="same")
    lo, hi = 3, 60
    trough = lo + int(np.argmin(smooth[lo:hi + 1]))
    print(f"\n7-day-smoothed minimum between day {lo} and {hi}: day {trough}")
    for d in range(max(0, trough - 10), min(120, trough + 15)):
        print(f"    day {d:>3}: raw {int(counts[d]):>6}  smooth {smooth[d]:>9.1f}")

    # cumulative shares at candidate cuts
    print("\nshare of gaps shorter than candidate cuts:")
    for cut in (7, 10, 14, 21, 28, 30, 45, 60):
        print(f"    <{cut:>2}d: {(gd < cut).mean() * 100:5.1f}%")


if __name__ == "__main__":
    main()
