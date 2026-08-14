"""Regression tests for reply-to-push matching — RUN2_PREREGISTRATION §9.6.

The seventh defect: the addr-route fallback credited ANY inbound from the recipient
within 90 days to the push, so on heavily-touched contacts it grabbed unrelated
conversations. Measured before the fix: 73% of addr-route replies had a subject that
did not match the opener; 195 of 1,322 replied=True rows (14.8%) were misattributed.

Every case below is a REAL pair from the corpus, found in the audit that caught the
defect. Same rules as the other test files: production functions only, and every
rejection test is paired with a positive control so the tests cannot be satisfied
by making the matcher reject everything.

Run: python3 -m pytest tests/test_reply_matching.py -v
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "scripts"))

from build_pushes import norm_subject, subjects_match  # noqa: E402  production


# ---------------------------------------------------------------------------
# Real misattributions from the corpus — these must now be REJECTED
# ---------------------------------------------------------------------------

def test_unrelated_reply_is_rejected():
    """'Intro Alec & Ross | AE @Encord' was credited with a reply titled 'job in sf'."""
    assert not subjects_match("job in sf", ["Intro Alec & Ross | AE @Encord"])


def test_cross_account_autoreply_is_rejected():
    """A CVPR dinner invite was credited with an auto-reply about a different account."""
    assert not subjects_match("Automatic reply: [EXT] Encord & SLB - working session",
                              ["[Invite] AI Leaders Dinner @ CVPR - 06/14"])


def test_calendar_booking_for_other_meeting_is_rejected():
    assert not subjects_match("Appointment booked: 30 min with Abhinay",
                              ["Zendesk <> Encord - catch up"])


def test_reply_to_other_push_is_rejected():
    assert not subjects_match("[Invite] Encord AI Leaders Dinner @ Promat",
                              ["Starling 2 Logis | Just onboarded Toyota-W"])


def test_empty_subject_is_unverifiable_and_rejected():
    assert not subjects_match("", ["Coffee @ NRF?"])
    assert not subjects_match(None, ["Coffee @ NRF?"])


# ---------------------------------------------------------------------------
# Positive controls — genuine replies that must still MATCH
# ---------------------------------------------------------------------------

def test_control_plain_re_reply_matches():
    assert subjects_match("Re: Coffee @ NRF?", ["Coffee @ NRF?"])


def test_control_punctuation_variant_matches():
    """Real near-miss: 'encord & tempo' answering '[Encord <> Tempo] Labelling and
    Fine-Tune' is the same conversation; punctuation must not break the tie."""
    assert subjects_match("encord & tempo",
                          ["[Encord <> Tempo] Labelling and Fine-Tune"])


def test_control_ooo_to_our_email_matches():
    """An out-of-office TO OUR EMAIL must stay a candidate (classifier labels it
    out_of_office, so it never counts as replied — but dropping it here would hide
    the OOO from the classifier entirely)."""
    assert subjects_match("Automatic reply: Encord - perception data annotation",
                          ["Encord - perception data annotation"])


def test_control_reply_to_followup_touch_matches():
    """A reply to follow-up #3 of the push is a reply to the push."""
    touches = ["Coffee @ NRF?", "Re: Coffee @ NRF?", "Encord x Acme - quick question"]
    assert subjects_match("RE: Encord x Acme - quick question", touches)


def test_control_forwarded_reply_matches():
    assert subjects_match("Fwd: Re: Coffee @ NRF?", ["Coffee @ NRF?"])


# ---------------------------------------------------------------------------
# The guard rails on the matcher itself
# ---------------------------------------------------------------------------

def test_short_containment_does_not_match():
    """'hi' appearing inside another subject is not a tie."""
    assert not subjects_match("hi", ["hiring ML engineers at Encord"])


def test_norm_strips_stacked_prefixes():
    assert norm_subject("RE: FW: Re: Automatic reply: Coffee @ NRF?") == "coffee nrf"


def test_norm_strips_bracket_tag_then_prefix():
    assert norm_subject("[EXT] RE: Coffee @ NRF?") == "coffee nrf"
