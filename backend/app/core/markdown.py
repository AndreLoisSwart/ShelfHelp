import re

# Markdown syntax that reads as noise in a one-line preview.
_MARKDOWN_NOISE = re.compile(
    # Line starts: checkbox (before plain bullets), heading, bullet, number, quote.
    r"^\s*([-*+] \[[ xX]\]|#{1,6}|[-*+]|\d+\.|>)\s+"
    # Emphasis and code marks, and links (keeping their text).
    r"|[*_`~]|\[([^\]]*)\]\([^)]*\)",
    re.M,
)


def plain_text(markdown: str) -> str:
    """Markdown as one line of plain text, for previews."""
    text = _MARKDOWN_NOISE.sub(lambda m: m.group(2) or "", markdown)
    return " ".join(text.split())
