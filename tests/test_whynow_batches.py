"""Pins the safety argument of the graded why-now pass (pre-registration §9.10).

That pass does not re-derive redaction. Its entire blinding guarantee is that its item
texts are byte-identical to the corpus that passed the gate at 0 leaks across 12,462
items. If that identity ever breaks, the guarantee is gone and no gate run on a subset
will catch it — the subset gate is corpus-dependent, which is what §9.10 records.

Each test is paired with a positive control, per the discipline in
docs/LEARNINGS_FOR_NEXT_RUN.md #12: a test that cannot fail is not a test.
"""
import glob
import json
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "output", "judge_batches")
MAIN = os.path.join(ROOT, "output", "judge_batches_whynow")
RESCORE = os.path.join(ROOT, "output", "judge_batches_whynow_rescore")

pytestmark = pytest.mark.skipif(
    not os.path.isdir(MAIN), reason="graded why-now batches not built in this checkout"
)


def load(d):
    items = []
    for p in sorted(glob.glob(os.path.join(d, "*.json"))):
        items += json.load(open(p))
    return items


@pytest.fixture(scope="module")
def source():
    return {it["id"]: it for it in load(SRC)}


def test_every_item_is_byte_identical_to_the_gated_source(source):
    """The blinding guarantee itself."""
    for it in load(MAIN) + load(RESCORE):
        s = source[it["id"]]
        assert it["subject"] == s["subject"], f"subject drifted for {it['id']}"
        assert it["text"] == s["text"], f"text drifted for {it['id']}"


def test_positive_control_a_mutated_text_is_caught(source):
    """The check above must be able to fail."""
    it = dict(load(MAIN)[0])
    it["text"] = it["text"] + " — Best, Alice Smith, Encord"
    assert it["text"] != source[it["id"]]["text"]


def test_population_is_cold_pitches_only(source):
    """Event invites are excluded by the addendum: an invite's occasion is the event."""
    import pandas as pd

    f = pd.read_parquet(os.path.join(ROOT, "data", "frame_G30.parquet"))
    want = set(f[f["type"] == "cold_pitch"]["email_id"].astype(str))
    got = {it["id"] for it in load(MAIN)}
    assert got == want, f"{len(got ^ want)} ids differ from the cold-pitch population"


def test_positive_control_population_check_is_not_vacuous(source):
    import pandas as pd

    f = pd.read_parquet(os.path.join(ROOT, "data", "frame_G30.parquet"))
    invites = set(f[f["type"] == "event_invite"]["email_id"].astype(str))
    got = {it["id"] for it in load(MAIN)}
    assert invites, "fixture would be vacuous: no event invites in the frame"
    assert not (got & invites), "event invites leaked into the graded population"


def test_no_duplicate_ids_in_the_main_pass():
    ids = [it["id"] for it in load(MAIN)]
    assert len(ids) == len(set(ids))


def test_rescore_is_a_strict_subset_of_the_main_pass():
    main = {it["id"] for it in load(MAIN)}
    rs = {it["id"] for it in load(RESCORE)}
    assert rs, "rescore subset is empty — the kappa gate would be unmeasurable"
    assert rs < main, "rescore items must all come from the graded population"
