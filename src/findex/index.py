
import argparse
import json
import pickle
import time
import tracemalloc
from collections import defaultdict
from pathlib import Path
from typing import Any

from findex.corpus import iter_documents
from findex.decorators import timed
from findex.index_model import DocMeta, Index, Posting
from findex.tokenize import tokenize_with_positions


@timed
def build_index(data_dir: Path) -> Index:
    positions_by_term: dict[str, dict[str, list[int]]] = defaultdict(dict)
    documents: dict[str, DocMeta] = {}

    for document in iter_documents(data_dir):
        token_count = 0

        for token, position in tokenize_with_positions(document.text):
            if document.doc_id not in positions_by_term[token]:
                positions_by_term[token][document.doc_id] = []

            positions_by_term[token][document.doc_id].append(position)
            token_count += 1

        documents[document.doc_id] = DocMeta(
            doc_id=document.doc_id,
            path=str(document.path),
            length=token_count,
        )

    sorted_index: dict[str, list[Posting]] = {}

    for term, document_positions in positions_by_term.items():
        sorted_index[term] = [
            Posting(
                doc_id=doc_id,
                frequency=len(positions),
                positions=tuple(positions),
            )
            for doc_id, positions in sorted(document_positions.items())
        ]

    return Index(sorted_index, documents)


def save_index(index: Index, output_path: Path) -> None:
    # Не завантажуй pickle-файли з невідомих джерел.
    with output_path.open("wb") as file:
        pickle.dump(index, file)


@timed
def load_index(input_path: Path) -> Index:
    with input_path.open("rb") as file:
        index = pickle.load(file)

    if not isinstance(index, Index):
        raise TypeError("File does not contain a valid Index")

    return index


def save_index_json(index: Index, output_path: Path) -> None:
    data: dict[str, Any] = {
        "index": {
            term: [
                {
                    "doc_id": posting.doc_id,
                    "frequency": posting.frequency,
                    "positions": list(posting.positions),
                }
                for posting in postings
            ]
            for term, postings in index.items()
        },
        "documents": {
            doc_id: {
                "doc_id": meta.doc_id,
                "path": meta.path,
                "length": meta.length,
            }
            for doc_id, meta in index.documents.items()
        },
    }

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False)


def load_index_json(input_path: Path) -> Index:
    with input_path.open("r", encoding="utf-8") as file:
        data: Any = json.load(file)

    postings = {
        term: [
            Posting(
                item["doc_id"],
                item["frequency"],
                tuple(item.get("positions", [])),
            )
            for item in items
        ]
        for term, items in data["index"].items()
    }

    documents = {
        doc_id: DocMeta(
            meta["doc_id"],
            meta["path"],
            meta["length"],
        )
        for doc_id, meta in data["documents"].items()
    }

    return Index(postings, documents)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build an inverted index")
    parser.add_argument("data_dir", type=Path)
    parser.add_argument("--out", type=Path, default=Path("index.bin"))
    parser.add_argument("--json-out", type=Path, default=Path("index.json"))
    args = parser.parse_args()

    tracemalloc.start()
    start = time.perf_counter()

    index = build_index(args.data_dir)
    documents = index.documents
    build_time = time.perf_counter() - start

    start = time.perf_counter()
    save_index(index, args.out)
    pickle_save_time = time.perf_counter() - start

    start = time.perf_counter()
    save_index_json(index, args.json_out)
    json_save_time = time.perf_counter() - start

    _, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(f"Documents: {len(documents)}")
    print(f"Unique terms: {len(index)}")
    print(f"Build time: {build_time:.2f} seconds")
    print(f"Peak memory: {peak_memory / 1024 / 1024:.2f} MB")

    print("\nPickle:")
    print(f"Save time: {pickle_save_time:.2f} seconds")
    print(f"File size: {args.out.stat().st_size / 1024 / 1024:.2f} MB")

    print("\nJSON:")
    print(f"Save time: {json_save_time:.2f} seconds")
    print(f"File size: {args.json_out.stat().st_size / 1024 / 1024:.2f} MB")


if __name__ == "__main__":
    main()
