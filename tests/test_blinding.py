"""Regression tests for judge blinding — RUN2_PREREGISTRATION §5.4.

§5.4 names two failure directions and treats both as damaging:

  UNDER-redaction  sender identity survives -> the judge can see who wrote the email,
                   which breaks rule 1 of the study. Run 1 leaked into ~30% of items.
  OVER-redaction   ordinary words get replaced -> the judge rates mangled text.
                   Run 1: an owner surnamed "Short" turned "a short call" into
                   "a [SENDER] call".

These tests pin both directions. As in test_features.py, every fix test is paired
with a positive control, so tightening a pattern cannot silently disable redaction.

Run: python3 -m pytest tests/test_blinding.py -v
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "scripts"))

import build_judge_batches as bjb  # noqa: E402  production redaction


# ---------------------------------------------------------------------------
# Over-redaction: recipient name / company must match on word boundaries.
# ---------------------------------------------------------------------------

def test_two_letter_name_does_not_eat_ordinary_words():
    """Recipient 'Al' must not turn 'also' into '[NAME]so'."""
    out = bjb.redact_names("We also work with perception teams.", "Al", "")
    assert out == "We also work with perception teams.", out


def test_control_two_letter_name_is_still_redacted():
    """Positive control: the actual name must still be replaced."""
    out = bjb.redact_names("Hi Al, quick thought.", "Al", "")
    assert out == "Hi [NAME], quick thought.", out


def test_short_company_does_not_eat_verb():
    """Company 'Speak' must not turn 'speaking' into '[COMPANY]ing'."""
    out = bjb.redact_names("Worth speaking about your pipeline?", "", "Speak")
    assert out == "Worth speaking about your pipeline?", out


def test_control_short_company_is_redacted_when_capitalised():
    out = bjb.redact_names("I have followed Speak for a while.", "", "Speak")
    assert out == "I have followed [COMPANY] for a while.", out


def test_control_multiword_company_redacted_case_insensitively():
    out = bjb.redact_names("your team at boston dynamics", "", "Boston Dynamics")
    assert out == "your team at [COMPANY]", out


def test_name_redaction_is_case_insensitive():
    out = bjb.redact_names("hi sarah, and Sarah again", "Sarah", "")
    assert out == "hi [NAME], and [NAME] again", out


# ---------------------------------------------------------------------------
# Under-redaction: the things §5.4 scans for must actually be removed.
# ---------------------------------------------------------------------------

SIGNED = """Hi Sarah,

We help perception teams cut labelling review time on large video datasets.

Would you be open to a short call on 2026-03-14?

Best,
Alexandra
AI // ML // Computer Vision @ Encord
Email: alexandra@tryencord.com
Website: https://encord.com
"""


def _redact_signed():
    bjb.SENDER_VOCAB = ["alexandra"]          # pruned vocab, as the builder passes it
    return bjb.redact(SIGNED, "Sarah", "")


def test_signature_block_is_removed():
    out = _redact_signed()
    assert "tryencord.com" not in out
    assert "Website" not in out


def test_sender_name_does_not_survive():
    out = _redact_signed()
    assert "alexandra" not in out.lower(), out


def test_urls_emails_and_iso_dates_are_placeheld():
    out = _redact_signed()
    assert "https://" not in out
    assert "@" not in out
    assert "2026-03-14" not in out
    assert "[DATE]" in out


def test_control_body_content_survives_redaction():
    """Positive control: the text the judge must rate is still there."""
    out = _redact_signed()
    assert "perception teams" in out
    assert "labelling review time" in out
    assert "open to a short call" in out
    assert "[NAME]" in out


# ---------------------------------------------------------------------------
# Frequency pruning — the mechanism that stops "Short" being redacted at all.
# ---------------------------------------------------------------------------

def test_prune_drops_tokens_that_are_ordinary_english():
    """A surname appearing in >2% of emails is vocabulary, not identity."""
    texts = ["please book a short call with the team"] * 50 + ["unrelated body text"] * 50
    kept = bjb.prune_common_words({"short", "kowalczyk"}, texts)
    assert "short" not in kept, kept
    assert "kowalczyk" in kept, kept


def test_prune_keeps_rare_names():
    texts = ["a body with no names in it at all"] * 100
    kept = bjb.prune_common_words({"alexandra", "hugo"}, texts)
    assert set(kept) == {"alexandra", "hugo"}, kept
