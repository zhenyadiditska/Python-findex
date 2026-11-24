
from pathlib import Path
from typing import Literal

import pytest

from findex.index import (
    build_index,
    load_index,
    load_index_json,
    save_index,
    save_index_json,
)
from findex.index_model import Index


def test_build_index(sample_documents: Path) -> None:
    index = build_index(sample_documents)

    assert index.num_docs == 3
    assert "python" in index
    assert len(index) > 0


def test_build_index_postings_are_sorted(sample_documents: Path) -> None:
    index = build_index(sample_documents)

    for postings in index.postings.values():
        doc_ids = [posting.doc_id for posting in postings]
        assert doc_ids == sorted(doc_ids)


def test_build_index_contains_document_metadata(
    sample_documents: Path,
) -> None:
    index = build_index(sample_documents)

    assert len(index.documents) == 3

    for doc_id, document in index.documents.items():
        assert doc_id == document.doc_id
        assert document.length > 0


@pytest.mark.parametrize("format_name", ["pickle", "json"])
def test_save_and_load_index(
    sample_index: Index,
    tmp_path: Path,
    format_name: Literal["pickle", "json"],
) -> None:
    output_path = tmp_path / (
        "index.bin" if format_name == "pickle" else "index.json"
    )

    if format_name == "pickle":
        save_index(sample_index, output_path)
        loaded_index = load_index(output_path)
    else:
        save_index_json(sample_index, output_path)
        loaded_index = load_index_json(output_path)

    assert loaded_index.postings == sample_index.postings
    assert loaded_index.documents == sample_index.documents
