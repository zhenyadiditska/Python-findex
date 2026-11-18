
from dataclasses import dataclass
from pathlib import Path
from collections import defaultdict, Counter
import pickle
import json
import time
import argparse
import tracemalloc
import sys


@dataclass(frozen=True, slots=True)
class Posting:
    doc_id: str
    frequency: int


@dataclass(frozen=True, slots=True)
class DocMeta:
    doc_id: str
    path: str
    length: int


if __name__ == "__main__":
    sys.modules["findex.index"] = sys.modules["__main__"]
    Posting.__module__ = "findex.index"
    DocMeta.__module__ = "findex.index"


from findex.corpus import iter_documents
from findex.tokenize import tokenize


def build_index(data_dir: Path):
    index = defaultdict(Counter)
    documents = {}

    for document in iter_documents(data_dir):
        token_count = 0

        for token in tokenize(document.text):
            index[token][document.doc_id] += 1
            token_count += 1

        documents[document.doc_id] = DocMeta(
            doc_id=document.doc_id,
            path=str(document.path),
            length=token_count
        )

    sorted_index = {}

    for term, frequencies in index.items():
        sorted_index[term] = [
            Posting(doc_id, frequency)
            for doc_id, frequency in sorted(frequencies.items())
        ]

    return sorted_index, documents


def save_index(index, documents, output_path: Path):
    # Не можна завантажувати pickle-файли з невідомих джерел:
    # вони можуть містити небезпечний код.
    with output_path.open("wb") as file:
        pickle.dump((index, documents), file)


def load_index(input_path: Path):
    with input_path.open("rb") as file:
        return pickle.load(file)


def save_index_json(index, documents, output_path: Path):
    data = {
        "index": {
            term: [
                {
                    "doc_id": posting.doc_id,
                    "frequency": posting.frequency
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
            for doc_id, meta in documents.items()
        }
    }

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False)


def load_index_json(input_path: Path):
    with input_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    index = {
        term: [
            Posting(item["doc_id"], item["frequency"])
            for item in postings
        ]
        for term, postings in data["index"].items()
    }

    documents = {
        doc_id: DocMeta(
            meta["doc_id"],
            meta["path"],
            meta["length"]
        )
        for doc_id, meta in data["documents"].items()
    }

    return index, documents


def main():
    parser = argparse.ArgumentParser(description="Build an inverted index")
    parser.add_argument("data_dir", type=Path)
    parser.add_argument("--out", type=Path, default=Path("index.bin"))
    parser.add_argument("--json-out", type=Path, default=Path("index.json"))
    args = parser.parse_args()

    tracemalloc.start()
    start = time.perf_counter()

    index, documents = build_index(args.data_dir)
    build_time = time.perf_counter() - start

    start = time.perf_counter()
    save_index(index, documents, args.out)
    pickle_save_time = time.perf_counter() - start

    start = time.perf_counter()
    save_index_json(index, documents, args.json_out)
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
