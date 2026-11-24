
from pathlib import Path

import pytest

from findex.index_model import DocMeta, Index, Posting


@pytest.fixture
def sample_index() -> Index:
    documents = {
        "doc1": DocMeta("doc1", "doc1.txt", 3),
        "doc2": DocMeta("doc2", "doc2.txt", 3),
        "doc3": DocMeta("doc3", "doc3.txt", 2),
        "doc4": DocMeta("doc4", "doc4.txt", 4),
    }

    postings = {
        "python": [
            Posting("doc1", 2, (0, 2)),
            Posting("doc2", 1, (0,)),
            Posting("doc4", 3, (0, 1, 2)),
        ],
        "django": [
            Posting("doc2", 2, (1, 2)),
            Posting("doc3", 1, (0,)),
        ],
        "async": [
            Posting("doc1", 1, (1,)),
            Posting("doc3", 1, (1,)),
        ],
    }

    return Index(postings, documents)


@pytest.fixture
def sample_documents(tmp_path: Path) -> Path:
    documents = {
        "python.txt": "Python is a programming language.",
        "django.txt": "Django is a Python web framework.",
        "async.txt": "Python supports asynchronous programming.",
    }

    for filename, content in documents.items():
        (tmp_path / filename).write_text(
            content,
            encoding="utf-8",
        )

    return tmp_path
