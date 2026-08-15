"""Regression tests for the six blinding defects found at judge-build time (§9.7).

Same discipline as tests/test_features.py:

  1. Every test calls the PRODUCTION function. None re-implements the logic. Run 1's
     audit tool re-derived text with its own regex and therefore agreed with nothing
     that was actually stored (docs/LEARNINGS_FOR_NEXT_RUN.md #12).

  2. Every defect test is PAIRED WITH A POSITIVE CONTROL. "The sender's name is gone"
     passes trivially if redaction deletes everything; the control asserts the body a
     judge must rate is still there. A redaction test without a control is satisfied by
     returning the empty string.

The defects, all found by READING built judge items before any judging was paid for:

  D8  prune_common_words used corpus frequency as a proxy for "ordinary English", so a
      prolific rep's surname was pruned for being frequent — 29.8% of items carried a
      sender name, the run-1 leak rate reproduced by the fix meant to prevent it.
  D9  the subject line never had EMAIL_RE applied, shipping 'james.sweeney@encord.com'.
  D10 split_signature missed curly apostrophes, non-English sign-offs, and sign-offs
      with a trailing clause, leaving whole signature blocks in place.
  D11 check_blinding.py pruned the vocabulary it was auditing — blind to D8 by
      construction.
  D12 a bare domain typed as prose ('Encord.com') has no scheme, so URL_RE missed it.
  D13 the recipient greeting kept a real first name whenever HubSpot held no firstname
      or the rep used a nickname ('Hi Ed' vs record 'Edward').
"""
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                "scripts"))
import build_judge_batches as bjb
from text_clean import split_signature, split_signature_strict


# --- D8: pruning must not treat a frequent name as an ordinary word ------------------

def test_d8_prolific_surname_is_not_pruned():
    """A surname in 30% of emails is still a surname. Frequency is not word-ness."""
    texts = ["Best regards, Charlotte Decaudaveine"] * 30 + ["A plain email about data"] * 70
    kept = set(bjb.prune_common_words({"decaudaveine", "charlotte"}, texts))
    assert "decaudaveine" in kept, "a surname was pruned for being frequent (D8)"
    assert "charlotte" in kept


def test_d8_control_real_word_is_still_pruned():
    """POSITIVE CONTROL: the rule must still protect ordinary English, or it is just
    'redact everything' — which is how 'a short call' became 'a [SENDER] call'."""
    texts = [f"Can we book a short call about item {i}?" for i in range(40)]
    kept = set(bjb.prune_common_words({"short"}, texts))
    assert "short" not in kept, "ordinary word not pruned — over-redaction returns"


def test_d8_calendar_words_pruned():
    texts = ["The dinner is on Jan 23rd"] * 10
    assert "jan" not in set(bjb.prune_common_words({"jan"}, texts))


def test_d8_single_lowercase_typo_does_not_unblind():
    """One stray lowercase use must not be enough to declare a name a word."""
    texts = ["Best, Kirpalani"] * 40 + ["a note mentioning kirpalani once"]
    assert "kirpalani" in set(bjb.prune_common_words({"kirpalani"}, texts))


# --- D9 / D12: subject and bare-domain redaction -------------------------------------

def test_d9_subject_email_address_redacted():
    bjb.SENDER_VOCAB = []
    s = bjb.redact_subject(
        "Encord // Acme | Intro @ Mon 13 Jan 2025 2:30pm (GMT) (james.sweeney@encord.com)",
        "", "")
    assert "@encord.com" not in s and "sweeney" not in s.lower(), "subject leaked an address (D9)"


def test_d9_control_subject_text_survives():
    """POSITIVE CONTROL: the subject must still be readable — it is scored."""
    bjb.SENDER_VOCAB = []
    s = bjb.redact_subject("Quick question about your labelling pipeline", "", "")
    assert s == "Quick question about your labelling pipeline"


def test_d12_bare_domain_redacted():
    bjb.SENDER_VOCAB = []
    for dom in ("Encord.com", "encord.ai", "cord.tech"):
        out = bjb.redact_subject(f"Have a look at {dom} for details", "", "")
        assert dom.lower() not in out.lower(), f"bare domain {dom} survived (D12)"


def test_d12_control_ordinary_sentence_untouched():
    bjb.SENDER_VOCAB = []
    assert bjb.redact_subject("Re: pricing", "", "") == "Re: pricing"


# --- D10: signature blocks must not survive on the judge path ------------------------

CURLY = "Hi there,\n\nWe should talk about your pipeline.\n\nHope all’s well,\nSkander\n\nSkander Fourati\n\nCommercial Associate"
FRENCH = "Bonjour,\n\nJe voulais vous parler de votre projet.\n\nÀ bientôt,\nCharlotte\n\nCharlotte Decaudaveine"
TRAILING = "Hi,\n\nWe reserved time for a demo on Wednesday.\n\nAll the best, and hopefully speak soon,\nJames Sweeney\n\nPartnerships Manager"

NAMES = {"skander", "fourati", "charlotte", "decaudaveine", "james", "sweeney"}


def test_d10_curly_apostrophe_signoff_cut():
    body, sig = split_signature_strict(CURLY, names=NAMES)
    assert "Fourati" not in body and "Skander" not in body, "signature survived (D10)"
    assert sig, "nothing was identified as a signature"


def test_d10_non_english_signoff_cut():
    body, _ = split_signature_strict(FRENCH, names=NAMES)
    assert "Decaudaveine" not in body and "Charlotte" not in body


def test_d10_signoff_with_trailing_clause_cut():
    body, _ = split_signature_strict(TRAILING, names=NAMES)
    assert "Sweeney" not in body and "Partnerships Manager" not in body


def test_d10_control_body_survives_all_three():
    """POSITIVE CONTROL: the sentence the judge rates must still be there. A splitter
    that returns '' passes every assertion above."""
    for text, needle in ((CURLY, "pipeline"), (FRENCH, "projet"), (TRAILING, "demo")):
        body, _ = split_signature_strict(text, names=NAMES)
        assert needle in body, f"strict splitter destroyed the body ({needle})"
        assert len(body.split()) >= 5


def test_d10_control_midbody_thanks_not_cut():
    """'Thanks for walking me through the pipeline' is a sentence, not a sign-off."""
    t = ("Hi,\n\nThanks for taking the time to walk me through your labelling setup last "
         "week, it was genuinely useful.\n\nCould we book 20 minutes?\n\nBest,\nNick")
    body, _ = split_signature_strict(t, names={"nick"})
    assert "20 minutes" in body, "a mid-body sentence was mistaken for a sign-off"


def test_d10_counting_splitter_left_untouched():
    """The FEATURE path must not move: Layer-1 results are committed against it."""
    body, _ = split_signature(CURLY)
    assert "Skander Fourati" in body, (
        "split_signature changed — feature counts and committed Layer-1 results depend "
        "on it; the strict variant is judge-only")


# --- D13: recipient greeting -------------------------------------------------------

def test_d13_greeting_name_redacted_without_contact_record():
    """HubSpot has no firstname for 2,209 contacts; the greeting must still be blinded."""
    for g in ("Hi Ed,", "Hey Poyraz,", "Bonjour Manon,", "Dear Guenter,"):
        out = bjb.redact_greeting(g + "\n\nsome body text")
        assert "[NAME]" in out.splitlines()[0], f"greeting name survived: {g} (D13)"


def test_d13_control_collective_greetings_not_mangled():
    """POSITIVE CONTROL: 'Hi team' / 'Hi both' are not names and must be left alone —
    over-redacting them would invent bespokeness where there is none."""
    for g in ("Hi team,", "Hi all,", "Hey both,", "Hi there,", "Dear Team,"):
        assert "[NAME]" not in bjb.redact_greeting(g + "\n\nbody"), f"over-redacted: {g}"


def test_d13_control_body_names_not_touched_by_greeting_rule():
    """The greeting rule is positional. It must not fire on prose mid-body."""
    t = "Hi [NAME],\n\nHeard great things about Skydio and Zipline this quarter."
    assert "Skydio" in bjb.redact_greeting(t) and "Zipline" in bjb.redact_greeting(t)


# --- D11: the gate must not prune the vocabulary it audits ---------------------------

def test_d11_check_uses_full_vocab_not_pruned():
    """The checker must search the FULL vocabulary.

    Pinned by reading the source: an audit that filters its search list through the
    heuristic it is auditing cannot fail on that heuristic's mistakes, which is exactly
    how 4,543 leaking items were reported clean.
    """
    src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "scripts", "check_blinding.py")).read()
    assert "full_vocab = bjb.build_sender_vocab()" in src
    assert "sorted(full_vocab)" in src, "checker is not iterating the unpruned vocabulary"
    assert re.search(r"pruned\s*=\s*full_vocab\s*-\s*kept", src), (
        "checker must still REPORT the pruning decision separately")
