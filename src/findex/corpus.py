
from pathlib import Path
from typing import NamedTuple, Iterator
import logging


logger = logging.getLogger(__name__)


class Document(NamedTuple):
    doc_id: str
    path: Path
    text: str


def iter_documents(root: Path) -> Iterator[Document]:
    """Read text documents one at a time from a directory tree."""

    for file_path in root.rglob("*.txt"):
        try:
            text = file_path.read_text(encoding="utf-8")

            yield Document(
                doc_id=file_path.relative_to(root).as_posix(),
                path=file_path,
                text=text
            )

        except (UnicodeDecodeError, OSError) as error:
            logger.warning("Could not read %s: %s", file_path, error)
            continue
