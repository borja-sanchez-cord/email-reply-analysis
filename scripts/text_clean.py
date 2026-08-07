"""Text cleaning shared by classification, features and judging.

Two jobs:
  1. html_to_text — usable plain text from hs_email_html when hs_email_text is absent.
  2. strip_quoted — remove quoted trails ("On ... wrote:", "-----Original Message-----",
     "From: ... Sent: ...", "> " lines) so the reply classifier NEVER sees the outgoing
     email it is replying to (blinding rule), and so opener features aren't computed
     over quoted text.
  3. strip_signature — heuristic signature/footer removal for feature computation.

Every heuristic here gets audited by printing examples before results are trusted
(see scripts/audit_features.py).
"""
import re
from html import unescape
from html.parser import HTMLParser


class _HTMLText(HTMLParser):
    """HTML -> text, recording WHERE each formatting event happens.

    Offsets are positions in the emitted text, so callers can count only the
    events that fall inside the message body (signatures carry logo images and
    bold contact lines that must not be counted as body formatting).
    """
    BLOCK = {"p", "div", "br", "li", "tr", "table", "h1", "h2", "h3", "h4", "blockquote"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.skip_depth = 0
        self.links = []          # (offset, href)
        self.images = []         # offsets
        self.bullets = []        # offsets
        self.bold_runs = []      # (offset, n_chars)
        self._bold_depth = 0

    @property
    def _pos(self):
        return sum(len(x) for x in self.parts)

    def handle_starttag(self, tag, attrs):
        if tag in ("style", "script", "head"):
            self.skip_depth += 1
        if tag == "a":
            href = dict(attrs).get("href", "")
            if href and not href.startswith("mailto:"):
                self.links.append((self._pos, href))
        if tag == "img":
            self.images.append(self._pos)
        if tag == "li":
            self.bullets.append(self._pos)
            self.parts.append("\n• ")
        if tag in ("b", "strong"):
            self._bold_depth += 1
        if tag in self.BLOCK:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in ("style", "script", "head") and self.skip_depth:
            self.skip_depth -= 1
        if tag in ("b", "strong") and self._bold_depth:
            self._bold_depth -= 1
        if tag in self.BLOCK:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.skip_depth:
            if self._bold_depth and data.strip():
                self.bold_runs.append((self._pos, len(data.strip())))
            self.parts.append(data)


def html_to_text(html):
    """Returns (raw_text, meta). meta carries offset-tagged formatting events in
    raw_text coordinates: links [(off, href)], images [off], bullets [off],
    bold_runs [(off, n_chars)]. raw_text is NOT whitespace-normalised, so the
    offsets stay valid; callers normalise their own copy for reading."""
    p = _HTMLText()
    try:
        p.feed(html or "")
    except Exception:
        return unescape(re.sub(r"<[^>]+>", " ", html or "")), {}
    raw_text = "".join(p.parts)
    return raw_text, {"links": p.links, "images": p.images,
                      "bullets": p.bullets, "bold_runs": p.bold_runs}


def tidy(text):
    """Whitespace-normalise text for reading/measuring (offsets not preserved)."""
    text = re.sub(r"[ \t]+", " ", text or "")
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)
    return text.strip()


QUOTE_STARTERS = [
    re.compile(r"^On .{5,120}(wrote|écrit)\s*:\s*$", re.I),
    re.compile(r"^-{2,}\s*Original Message\s*-{2,}", re.I),
    re.compile(r"^-{2,}\s*Forwarded message\s*-{2,}", re.I),
    re.compile(r"^From:\s*.+", re.I),
    re.compile(r"^Von:\s*.+", re.I),
    re.compile(r"^De\s*:\s*.+", re.I),
    re.compile(r"^_{10,}\s*$"),
    re.compile(r"^Sent from my ", re.I),
    re.compile(r"^Get Outlook for ", re.I),
]


#  "On Thu, 13 Feb 2025 at 13:02, Someone\n<addr> wrote:"  — the header often wraps
#  across two or three lines, so it must be matched on the joined text, not line by line.
MULTILINE_QUOTE_RE = re.compile(
    r"\n\s*On .{0,200}?\bwrote\s*:", re.S | re.I)


def strip_quoted(text):
    """Cut everything from the first quoted-trail marker onward; drop '>' lines."""
    text = MULTILINE_QUOTE_RE.split(text or "", maxsplit=1)[0]
    lines = (text or "").splitlines()
    out = []
    for i, ln in enumerate(lines):
        s = ln.strip()
        hit = False
        for pat in QUOTE_STARTERS[:7]:  # trail markers end the message entirely
            if pat.match(s):
                # "From:" only counts as a trail if a Sent/Date/To line follows soon
                if pat.pattern.startswith("^From:"):
                    nxt = " ".join(l.strip() for l in lines[i + 1:i + 4])
                    if not re.search(r"^(Sent|Date|To|Subject)\s*:", nxt, re.I) and \
                       not re.search(r"\b(Sent|Date|To)\s*:", nxt, re.I):
                        continue
                hit = True
                break
        if hit:
            break
        if s.startswith(">"):
            continue
        out.append(ln)
    res = "\n".join(out)
    res = re.sub(r"\n\s*\n\s*\n+", "\n\n", res)
    return res.strip()


def unwrap(text):
    """Join hard-wrapped lines within a paragraph.

    Plaintext mail from Gmail/Outlook is hard-wrapped at ~72 chars, so a single
    sentence spans several lines. Splitting on newlines would count lines as
    sentences and truncate questions at the wrap point ("...grab a\\ncoffee?"),
    which would make plaintext emails look systematically different from HTML
    ones. Blank lines (paragraph breaks) and bullet lines are preserved.
    """
    out = []
    for para in re.split(r"\n\s*\n", text or ""):
        lines = [l.rstrip() for l in para.splitlines()]
        buf = []
        for ln in lines:
            s = ln.strip()
            if not s:
                continue
            # bullets and lines that look like list items stay on their own line
            if re.match(r"^([•\-\*•]|\d+[\.\)])\s+", s):
                buf.append("\n" + s)
            elif buf and not buf[-1].endswith(("\n",)) and not re.search(r"[.!?:;]$", buf[-1]):
                buf[-1] = buf[-1] + " " + s
            else:
                buf.append(s)
        para_txt = " ".join(x.lstrip() if not x.startswith("\n") else x for x in buf)
        para_txt = re.sub(r"[ \t]+", " ", para_txt).strip()
        if para_txt:
            out.append(para_txt)
    return "\n\n".join(out)


SIGNOFF_RE = re.compile(
    r"^(best|best regards|kind regards|regards|thanks|thank you|many thanks|cheers|"
    r"warm regards|all the best|sincerely|thanks so much|thanks|br|rgds|speak soon|"
    r"chat soon|talk soon|looking forward|hope all'?s well|hope this helps|"
    r"appreciate it|much appreciated|yours|warmly|thx)\b[\s,!.–-]*$", re.I)

# Standard signature delimiter, or the start of a contact block.
SIG_DELIM_RE = re.compile(r"^\s*(--+|__+|—+)\s*$")
CONTACT_LINE_RE = re.compile(
    r"^\s*(email|e-mail|website|web|address|linkedin|phone|tel|telephone|mobile|"
    r"cell|book a (call|meeting)|calendar|schedule a call)\s*[:|]", re.I)
# Title lines used by this org's signatures, e.g. "AI // ML // Computer Vision @ Encord",
# "Partnerships Manager @ Encord", "Growth at Encord".
ORG_TITLE_RE = re.compile(r"^\s*[^\n]{0,60}\s(@|at)\s+Encord\s*$", re.I)


def split_signature(text):
    """Return (body, signature).

    The signature starts at the EARLIEST of: a standard delimiter line ("--"),
    a sign-off line, a contact-block line ("Email:", "Website:", ...), or an
    org title line ("... @ Encord") — searched only in the last 60% of the
    message so a mid-body "thanks" never truncates the content.

    Getting this wrong leaks signature markup into body formatting counts
    (audit finding: signature logos and bold title lines inflated has_bold to
    77% and n_images to 75% of all emails).
    """
    lines = (text or "").splitlines()
    n = len(lines)
    start = max(2, int(n * 0.4))
    for i, ln in enumerate(lines):
        if i < start:
            continue
        s = ln.strip()
        if not s:
            continue
        if (SIG_DELIM_RE.match(s) or SIGNOFF_RE.match(s)
                or CONTACT_LINE_RE.match(s) or ORG_TITLE_RE.match(s)):
            return "\n".join(lines[:i]).strip(), "\n".join(lines[i:]).strip()
    return (text or "").strip(), ""
