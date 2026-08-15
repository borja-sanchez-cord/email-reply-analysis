"""Automated blinding leak check — RUN2_PREREGISTRATION §5.4. BLOCKS the judge launch.

In run 1 sender names leaked into ~30% of judge items through signature blocks the
sign-off detector missed. A judge that can see who wrote an email breaks rule 1 of the
study. This script runs over the BUILT batches before any judge agent starts, and exits
non-zero on any hit.

It imports the vocabulary functions from scripts/build_judge_batches.py rather than
re-deriving them. Run 1's audit tool re-implemented its own text derivation and therefore
disagreed with what was actually stored — an audit that doesn't call the production code
audits nothing (docs/LEARNINGS_FOR_NEXT_RUN.md #12).

Two directions are reported, because §5.4 names both as damaging:
  LEAKS          identity that survived redaction  -> hard failure, blocks launch
  OVER-REDACTION placeholder soup that destroys the text the judge must rate
                 -> reported loudly, does not block (a judgement call, not a rule breach)

Usage: python3 check_blinding.py [output/judge_batches ...]
Exit:  0 = clean, 1 = leaks found (do not launch)
"""
import glob
import json
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_judge_batches as bjb  # production redaction vocabulary

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "output")

# The four internal sending domains (docs/LEARNINGS_FOR_NEXT_RUN.md #1). A bare domain
# surviving in the text means the signature split failed, which is the run-1 leak.
INTERNAL_DOMAINS = ["encord.com", "encord.ai", "tryencord.com", "cord.tech"]

CHECKS = [
    ("email address", re.compile(r"[A-Za-z0-9._%+\-']+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")),
    ("raw URL", re.compile(r"(https?://|www\.)\S+", re.I)),
    ("internal domain", re.compile("|".join(re.escape(d) for d in INTERNAL_DOMAINS), re.I)),
    ("ISO date", re.compile(r"\b20\d\d[-/]\d\d[-/]\d\d\b")),
    ("quote header", re.compile(r"\bwrote\s*:", re.I)),
]

PLACEHOLDER_RE = re.compile(r"\[(NAME|COMPANY|LINK|EMAIL|DATE|SENDER)\]")


def load(dirs):
    items = []
    for d in dirs:
        paths = sorted(glob.glob(os.path.join(d, "batch_*.json")))
        if not paths:
            print(f"!! no batch files in {d}")
        for p in paths:
            for x in json.load(open(p)):
                items.append((os.path.basename(p), x))
    return items


def main():
    dirs = sys.argv[1:] or [os.path.join(OUT, "judge_batches")]
    items = load(dirs)
    if not items:
        print("FAIL: nothing to check — build the batches first")
        return 1
    print(f"checking {len(items)} judge items across {len(dirs)} dir(s)\n")

    # RUN2_PREREGISTRATION §9.7 — THE CHECK USES THE FULL, UNPRUNED VOCABULARY.
    #
    # This script previously called prune_common_words() and then searched only for what
    # survived pruning. That made the gate blind to the builder's own worst failure mode:
    # any token the builder wrongly decided was an ordinary word was, by construction,
    # also a token the checker would not look for. The builder pruned `decaudaveine`,
    # `fourati`, `kirpalani` and `ulrik` — real surnames — and the gate reported those
    # 4,543 affected items as clean. An audit that inherits the assumption it is auditing
    # cannot fail (docs/LEARNINGS_FOR_NEXT_RUN.md #12; §9.4 is the same defect class).
    #
    # Now: every token is searched. Hits are split into two classes so the pruning
    # DECISION is visible and reviewable rather than silent.
    texts = [(x.get("subject", "") + " " + x.get("text", "")) for _, x in items]
    full_vocab = bjb.build_sender_vocab()
    scrub = [bjb.EMAIL_RE.sub(" ", bjb.URL_RE.sub(" ", t)) for t in texts]
    kept = set(bjb.prune_common_words(full_vocab, scrub))
    pruned = full_vocab - kept
    vocab_res = [(t, re.compile(rf"\b{re.escape(t)}\b", re.I)) for t in sorted(full_vocab)]

    leaks = Counter()
    warn = Counter()
    examples = {}
    name_hits = Counter()
    pruned_hits = Counter()

    for batch, x in items:
        blob = (x.get("subject", "") or "") + "\n" + (x.get("text", "") or "")
        for label, rx in CHECKS:
            m = rx.search(blob)
            if m:
                leaks[label] += 1
                examples.setdefault(label, []).append((batch, x["id"], m.group(0)[:80]))
        hit_ident = hit_pruned = False
        for tok, rx in vocab_res:
            m = rx.search(blob)
            if not m:
                continue
            if tok in kept:
                if not hit_ident:
                    leaks["sender name token"] += 1
                    examples.setdefault("sender name token", []).append(
                        (batch, x["id"], m.group(0)[:80]))
                hit_ident = True
                name_hits[tok] += 1
            else:
                if not hit_pruned:
                    warn["pruned-as-ordinary token"] += 1
                hit_pruned = True
                pruned_hits[tok] += 1

    print("=== LEAK CHECK (any non-zero blocks the launch) ===")
    for label, _ in CHECKS:
        print(f"  {label:<18} {leaks[label]:>6}")
    print(f"  {'sender name token':<18} {leaks['sender name token']:>6}")

    for label, ex in examples.items():
        print(f"\n  --- {label}: first {min(8, len(ex))} of {len(ex)} ---")
        for b, i, s in ex[:8]:
            print(f"      {b} {i}: {s!r}")
    if name_hits:
        print(f"\n  sender tokens that leaked, by frequency: {name_hits.most_common(20)}")

    print("\n=== PRUNED-AS-ORDINARY (reported, does not block — REVIEW THIS LIST) ===")
    print(f"  tokens the builder chose not to redact: {sorted(pruned)}")
    print(f"  items containing one: {warn['pruned-as-ordinary token']} of {len(items)} "
          f"({100 * warn['pruned-as-ordinary token'] / len(items):.1f}%)")
    if pruned_hits:
        print(f"  by frequency: {pruned_hits.most_common(25)}")
    print("  Every entry must be a word a judge would read as ordinary English or a "
          "calendar term.\n  A surname here means the pruning rule is wrong again (§9.7).")

    print("\n=== OVER-REDACTION (reported, does not block) ===")
    heavy = []
    for batch, x in items:
        t = x.get("text", "") or ""
        toks = t.split()
        if not toks:
            continue
        share = len(PLACEHOLDER_RE.findall(t)) / len(toks)
        heavy.append((share, batch, x["id"], t))
    heavy.sort(reverse=True)
    over = [h for h in heavy if h[0] > 0.15]
    print(f"  items >15% placeholder tokens: {len(over)} of {len(items)} "
          f"({100 * len(over) / len(items):.1f}%)")
    print(f"  worst 10 (read these — this is how 'a short call' became 'a [SENDER] call'):")
    for share, batch, i, t in heavy[:10]:
        print(f"    {share:.0%} {batch} {i}: {t[:150]!r}")

    empt = sum(1 for _, x in items if not (x.get("text") or "").strip())
    print(f"\n  empty text after redaction: {empt}")

    total = sum(leaks.values())
    print(f"\n{'=' * 60}")
    if total:
        print(f"BLOCKED: {total} leak hits across {len(items)} items. "
              f"Fix the redaction and rebuild — do not launch the judges.")
        return 1
    print(f"CLEAN: 0 leaks across {len(items)} items. Judges may launch.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
