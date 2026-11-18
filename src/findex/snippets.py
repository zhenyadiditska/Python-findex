import re
from pathlib import Path


def make_snippet(path, terms, window=80):
    path = Path(path)

    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""

    if not terms:
        return text[:window * 2]

    words = [
        term.casefold()
        for term in terms
        if term.strip()
    ]

    if not words:
        return text[:window * 2]

    pattern = re.compile(
        r"(?<!\w)("
        + "|".join(
            re.escape(term)
            for term in sorted(words, key=len, reverse=True)
        )
        + r")(?!\w)",
        re.IGNORECASE
    )

    match = pattern.search(text)

    if not match:
        return text[:window * 2]

    start = max(0, match.start() - window)
    end = min(len(text), match.end() + window)
    snippet = text[start:end]

    if start > 0:
        snippet = "..." + snippet

    if end < len(text):
        snippet += "..."

    return pattern.sub(
        lambda item: f"**{item.group()}**",
        snippet
    )
