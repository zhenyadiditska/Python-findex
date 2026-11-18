import re
import unicodedata
from typing import Iterator


PATTERN = r"[^\W_]+(?:['’\-][^\W_]+)*"


def tokenize_with_positions(text: str) -> Iterator[tuple[str, int]]:
    """
    Split text into tokens and return their positions.
    """

    text = unicodedata.normalize("NFC", text)
    text = text.casefold()

    for position, match in enumerate(re.finditer(PATTERN, text)):
        yield match.group(), position


def tokenize(text: str) -> Iterator[str]:
    """
    Split text into tokens.
    """

    for token, _ in tokenize_with_positions(text):
        yield token
