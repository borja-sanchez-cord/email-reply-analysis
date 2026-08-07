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
    BLOCK = {"p", "div", "br", "li", "tr", "table", "h1", "h2", "h3", "h4", "blockquote"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.skip_depth = 0
        self.links = []
        self.n_images = 0
        self.n_bullets = 0
        self.bold_chars = 0
        self._bold_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("style", "script", "head"):
            self.skip_depth += 1
        if tag == "a":
            href = dict(attrs).get("href", "")
            if href and not href.startswith("mailto:"):
                self.links.append(href)
        if tag == "img":
            self.n_images += 1
        if tag == "li":
            self.n_bullets += 1
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
            self.parts.append(data)
            if self._bold_depth:
                self.bold_chars += len(data.strip())


def html_to_text(html):
    """Returns (text, meta) where meta has links/images/bullets/bold from markup."""
    p = _HTMLText()
    try:
        p.feed(html or "")
    except Exception:
        return unescape(re.sub(r"<[^>]+>", " ", html or "")), {}
    text = "".join(p.parts)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)
    return text.strip(), {"links": p.links, "n_images": p.n_images,
                          "n_bullets": p.n_bullets, "bold_chars": p.bold_chars}


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


def strip_quoted(text):
    """Cut everything from the first quoted-trail marker onward; drop '>' lines."""
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


SIGNOFF_RE = re.compile(
    r"^(best|best regards|kind regards|regards|thanks|thank you|many thanks|cheers|"
    r"warm regards|all the best|sincerely|thanks so much|thanks,|br|rgds)\b[,!.]?\s*$", re.I)


def split_signature(text):
    """Return (body, signature). Signature = from the sign-off line (in the last
    60% of the message) to the end, or trailing contact-info block."""
    lines = (text or "").splitlines()
    n = len(lines)
    for i, ln in enumerate(lines):
        if i >= max(2, int(n * 0.4)) and SIGNOFF_RE.match(ln.strip()):
            return "\n".join(lines[:i]).strip(), "\n".join(lines[i:]).strip()
    return (text or "").strip(), ""
