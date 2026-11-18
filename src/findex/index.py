from pathlib import Path
from collections import defaultdict
import pickle
import json
import time
import argparse
import tracemalloc

from findex.index_model import Index, Posting, DocMeta
from findex.corpus import iter_documents
from findex.tokenize import tokenize_with_positions
from findex.decorators import timed


@timed
def build_index(data_dir: Path):
    index = defaultdict(dict)
    documents = {}

    for document in iter_documents(data_dir):
        token_count = 0

        for token, position in tokenize_with_positions(document.text):
            if document.doc_id not in index[token]:
                index[token][document.doc_id] = []

            index[token][document.doc_id].append(position)
            token_count += 1

        documents[document.doc_id] = DocMeta(
            doc_id=document.doc_id,
            path=str(document.path),
            length=token_count
        )

    sorted_index = {}

    for term, document_positions in index.items():
        sorted_index[term] = [
            Posting(
                doc_id=doc_id,
                frequency=len(positions),
                positions=tuple(positions)
            )
            for doc_id, positions in sorted(document_positions.items())
        ]

    return Index(sorted_index, documents)


def save_index(index, output_path: Path):
    # Не завантажуй pickle-файли з невідомих джерел.
    with output_path.open("wb") as file:
        pickle.dump(index, file)


@timed
def load_index(input_path: Path):
    with input_path.open("rb") as file:
        return pickle.load(file)


def save_index_json(index, output_path: Path):
    data = {
        "index": {
            term: [
                {
                    "doc_id": posting.doc_id,
                    "frequency": posting.frequency,
                    "positions": list(posting.positions)
                }
                for posting in postings
            ]
            for term, postings in index.items()
        },
        "documents": {
            doc_id: {
                "doc_id": meta.doc_id,
                "path": meta.path,
                "length": meta.length
            }
            for doc_id, meta in index.documents.items()
        }
    }

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False)


def load_index_json(input_path: Path):
    with input_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    postings = {
        term: [
            Posting(
                item["doc_id"],
                item["frequency"],
                tuple(item.get("positions", []))
            )
            for item in items
        ]
        for term, items in data["index"].items()
    }

    documents = {
        doc_id: DocMeta(
            meta["doc_id"],
            meta["path"],
            meta["length"]
        )
        for doc_id, meta in data["documents"].items()
    }

    return Index(postings, documents)


def main():
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
