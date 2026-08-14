"""Regression tests for the five silent counter defects found in run 1.

Pre-registered in rules/RUN2_PREREGISTRATION.md §5.1. Written and passing BEFORE
the frame is rebuilt.

Two rules these tests follow, both learned the hard way:

  1. They import and call the PRODUCTION functions (scripts/features_compute.py,
     scripts/text_clean.py). Run 1's audit tool re-derived text with its own regex
     and therefore disagreed with what was actually stored in the parquet — the
     audit said one thing and the feature another. A test that re-implements the
     logic tests nothing.

  2. Every defect test is PAIRED WITH A POSITIVE CONTROL. Asserting
     "n_questions == 0 on a tracking URL" passes trivially if the question
     counter is broken and always returns 0. The control asserts the counter
     still fires on a real question. A defect test without a control is a test
     that can be satisfied by deleting the feature.

Run: python3 -m pytest tests/test_features.py -v
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "scripts"))

from features_compute import featurize  # noqa: E402  production function
from text_clean import split_signature, unwrap  # noqa: E402  production functions


def feat(text=None, html=None, subject="Quick question", contact=None):
    """Call the production featurizer exactly as the pipeline calls it."""
    rec = {"id": "test-1", "properties": {
        "hs_email_subject": subject,
        "hs_email_text": text or "",
        "hs_email_html": html or "",
    }}
    return featurize(rec, contact or {})


# ---------------------------------------------------------------------------
# Defect 1 — tracking URLs counted as questions, and inflating word counts.
# Run 1: "emails with a question" was 72% before the fix, 55% after. The same
# URLs added 30-80 words each.
# ---------------------------------------------------------------------------

URL_BODY = """Hi Sarah,

We are running a session on label quality for perception teams next month.

You can register on the page here:
https://encord.com/webinars/label-quality/?utm_source=hubspot&utm_medium=email&utm_campaign=q3_webinar_emea&hsa_acc=1234567890

Hope to see you there.

Best,
Alex
"""

REAL_QUESTION_BODY = """Hi Sarah,

We are running a session on label quality for perception teams next month.

Would you be interested in joining?

Hope to see you there.

Best,
Alex
"""


def test_defect1_tracking_url_is_not_a_question():
    """A '?' that only appears inside a ?utm_source= query string is not a question."""
    assert feat(text=URL_BODY)["n_questions"] == 0


def test_defect1_control_real_question_still_counted():
    """Positive control: the counter must still fire on a genuine question."""
    assert feat(text=REAL_QUESTION_BODY)["n_questions"] == 1


def test_defect1_tracking_url_does_not_inflate_word_count():
    """A long tracking URL collapses to one token, not 30-80 words.

    Compared against the same email with the URL replaced by a bare domain, so
    the assertion is about the query string specifically.
    """
    short = URL_BODY.replace(
        "https://encord.com/webinars/label-quality/?utm_source=hubspot"
        "&utm_medium=email&utm_campaign=q3_webinar_emea&hsa_acc=1234567890",
        "https://encord.com")
    assert feat(text=URL_BODY)["n_words"] == feat(text=short)["n_words"]


def test_defect1_url_still_counted_as_a_link():
    """Control: collapsing URLs for text measurement must not lose the link count."""
    assert feat(text=URL_BODY)["n_links"] == 1


# ---------------------------------------------------------------------------
# Defect 2 — unsubscribe / legal-confidentiality footers surviving the
# signature split, adding a question and ~60 words to every email carrying them.
# ---------------------------------------------------------------------------

CLEAN_BODY = """Hi Sarah,

We help perception teams cut labelling review time.

Would you be open to a short call?

Best,
Alex
"""

FOOTER_UNSUB = """
Is this email not relevant to you? Prefer fewer emails from me? You can let me
know at any time and I will take you off my list straight away.
"""

FOOTER_LEGAL = """
This email and any files transmitted with it are confidential and intended
solely for the use of the individual to whom they are addressed. If you have
received this email in error please notify the sender. Are you the intended
recipient?
"""


def test_defect2_unsub_footer_contributes_nothing():
    """Footer text must add 0 words and 0 questions."""
    base = feat(text=CLEAN_BODY)
    withf = feat(text=CLEAN_BODY + FOOTER_UNSUB)
    assert withf["n_words"] == base["n_words"]
    assert withf["n_questions"] == base["n_questions"]


def test_defect2_legal_footer_contributes_nothing():
    base = feat(text=CLEAN_BODY)
    withf = feat(text=CLEAN_BODY + FOOTER_LEGAL)
    assert withf["n_words"] == base["n_words"]
    assert withf["n_questions"] == base["n_questions"]


def test_defect2_control_body_question_survives():
    """Positive control: the body's own question is not stripped along with the footer."""
    assert feat(text=CLEAN_BODY + FOOTER_UNSUB)["n_questions"] == 1


# ---------------------------------------------------------------------------
# Defect 3 — hard-wrapped plaintext. Gmail/Outlook wrap at ~72 chars, so
# splitting on newlines counts LINES as sentences and truncates questions at the
# wrap point (run 1 recorded questions as "coffee?"). This is a
# plaintext-vs-HTML difference masquerading as a writing-style difference, which
# makes it the most dangerous of the five.
# ---------------------------------------------------------------------------

UNWRAPPED = """Hi Sarah,

I noticed your team published a paper on robustness under distribution shift last month and it made me think of a problem several perception teams have raised with us recently.

Would you be open to a quick fifteen minute call next week to compare notes?

Best,
Alex
"""

WRAPPED = """Hi Sarah,

I noticed your team published a paper on robustness under distribution
shift last month and it made me think of a problem several perception
teams have raised with us recently.

Would you be open to a quick fifteen minute call next
week to compare notes?

Best,
Alex
"""


def test_defect3_wrapping_does_not_change_any_text_measure():
    """The same email wrapped and unwrapped must measure identically."""
    a, b = feat(text=UNWRAPPED), feat(text=WRAPPED)
    for k in ("n_words", "n_sentences", "n_questions", "first_question_words"):
        assert a[k] == b[k], f"{k}: unwrapped={a[k]} wrapped={b[k]}"


def test_defect3_question_is_not_truncated_at_the_wrap():
    """The question must survive whole, not be cut to its last line ('week to compare notes?')."""
    f = feat(text=WRAPPED)
    assert f["n_questions"] == 1
    # "Would you be open to a quick fifteen minute call next week to compare notes?"
    # = 15 words. The defect truncated it at the wrap to "week to compare notes?" = 4.
    assert f["first_question_words"] == 15, f["first_question_words"]


def test_defect3_wrapped_lines_are_not_sentences():
    """Three wrapped lines forming one sentence count as one, not three."""
    assert feat(text=WRAPPED)["n_sentences"] == 2


def test_defect3_unwrap_preserves_bullets():
    """Control: unwrap must not glue list items into the preceding paragraph."""
    out = unwrap("Here is the shape of it:\n\n- first point\n- second point\n- third point")
    assert out.count("- ") == 3, out


# ---------------------------------------------------------------------------
# Defect 4 — signature logos and bold job titles counted as body formatting.
# Run 1: has_bold was 77% and images appeared on 75% of emails; the bold text
# was 'AI // ML // Computer Vision @ Encord'. After the fix: 33% and 0.1/email.
# ---------------------------------------------------------------------------

HTML_SIG_ONLY = """<html><body>
<p>Hi Sarah,</p>
<p>We help perception teams cut labelling review time on large video datasets.</p>
<p>Several teams working on similar problems have found the review step is where
the time actually goes.</p>
<p>Would you be open to a short call?</p>
<p>Best,<br>Alex</p>
<div>
  <img src="https://encord.com/logo.png" width="120">
  <p><b>AI // ML // Computer Vision @ Encord</b></p>
  <p>Email: alex@encord.com</p>
</div>
</body></html>"""

HTML_BODY_FORMATTING = """<html><body>
<p>Hi Sarah,</p>
<p>We help perception teams cut <b>labelling review time</b> on large video datasets.</p>
<p>Several teams working on similar problems have found the review step is where
the time actually goes.</p>
<p><img src="https://encord.com/chart.png" width="400"></p>
<p>Would you be open to a short call?</p>
<p>Best,<br>Alex</p>
<div>
  <img src="https://encord.com/logo.png" width="120">
  <p><b>AI // ML // Computer Vision @ Encord</b></p>
</div>
</body></html>"""


def test_defect4_signature_bold_and_logo_are_not_body_formatting():
    f = feat(html=HTML_SIG_ONLY)
    assert f["has_bold"] is False, "signature job title counted as body bold"
    assert f["n_images"] == 0, "signature logo counted as a body image"


def test_defect4_control_real_body_formatting_still_counted():
    """Positive control: bold and images inside the body must still register."""
    f = feat(html=HTML_BODY_FORMATTING)
    assert f["has_bold"] is True
    assert f["n_images"] == 1, f["n_images"]


def test_defect4_signature_is_detected_at_all():
    """Control on the mechanism the other assertions depend on."""
    body, sig = split_signature(
        "Hi Sarah,\n\nOne\n\nTwo\n\nThree\n\nBest,\nAlex\nAI // ML // Computer Vision @ Encord")
    assert sig, "signature split found nothing"
    assert "Encord" not in body


# ---------------------------------------------------------------------------
# Defect 5 — short names and companies matching ordinary words. A contact named
# "Or" matched the word "or"; a company called "Speak" matched the verb.
# ---------------------------------------------------------------------------

SHORT_NAME_BODY = """Hi there,

We work with perception teams on labelling throughput, or on review quality
where that is the tighter constraint.

Happy to speak whenever suits you.

Best,
Alex
"""

# Same email, but the name and company genuinely do appear.
REAL_MENTION_BODY = """Hi Sarah,

I saw the news about Cohere last week and thought of you, Sarah.

We work with perception teams on labelling throughput.

Best,
Alex
"""


def test_defect5_two_letter_name_does_not_match_prose():
    """Contact 'Or' must not match the conjunction 'or'."""
    f = feat(text=SHORT_NAME_BODY, contact={"firstname": "Or", "company": "Speak"})
    assert f["greeting_has_name"] is False
    assert f["name_beyond_greeting"] is False


def test_defect5_short_common_word_company_does_not_match_verb():
    """Company 'Speak' must not match 'happy to speak'."""
    f = feat(text=SHORT_NAME_BODY, contact={"firstname": "Or", "company": "Speak"})
    assert f["mentions_company"] is False


def test_defect5_control_real_name_and_company_still_matched():
    """Positive control: the fix must not make these features always False."""
    f = feat(text=REAL_MENTION_BODY, contact={"firstname": "Sarah", "company": "Cohere"})
    assert f["greeting_has_name"] is True
    assert f["name_beyond_greeting"] is True
    assert f["mentions_company"] is True


def test_defect5_control_capitalised_short_company_still_matched():
    """A short company name IS matched when it appears capitalised as a name."""
    body = SHORT_NAME_BODY.replace("Happy to speak whenever suits you.",
                                   "I have been following Speak for a while.")
    f = feat(text=body, contact={"firstname": "Or", "company": "Speak"})
    assert f["mentions_company"] is True
