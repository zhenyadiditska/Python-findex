
import re
import unicodedata
from typing import Iterator


def tokenize(text: str) -> Iterator[str]:
    """
    Split text into tokens.

    Apostrophes and hyphens are kept inside words.
    Digits are treated as part of tokens.
    Punctuation and underscores are ignored.
    """

    text = unicodedata.normalize("NFC", text)
    text = text.casefold()

    pattern = r"[^\W_]+(?:['’\-][^\W_]+)*"

    for match in re.finditer(pattern, text):
        yield match.group()
