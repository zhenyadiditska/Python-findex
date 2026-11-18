
import argparse
import time
import tracemalloc
from pathlib import Path

from findex.index import load_index


def merge_and(left, right):
    result = []
    i = j = 0

    while i < len(left) and j < len(right):
        if left[i].doc_id == right[j].doc_id:
            result.append(left[i])
            i += 1
            j += 1
        elif left[i].doc_id < right[j].doc_id:
            i += 1
        else:
            j += 1

    return result


def merge_or(left, right):
    result = []
    i = j = 0

    while i < len(left) and j < len(right):
        if left[i].doc_id == right[j].doc_id:
            result.append(left[i])
            i += 1
            j += 1
        elif left[i].doc_id < right[j].doc_id:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    result.extend(left[i:])
    result.extend(right[j:])
    return result


def set_and(left, right):
    right_ids = {p.doc_id for p in right}
    return [p for p in left if p.doc_id in right_ids]


def set_or(left, right):
    combined = {p.doc_id: p for p in left}

    for posting in right:
        combined.setdefault(posting.doc_id, posting)

    return [combined[key] for key in sorted(combined)]


def merge_difference(left, right):
    result = []
    i = j = 0

    while i < len(left):
        if j >= len(right):
            result.extend(left[i:])
            break

        if left[i].doc_id == right[j].doc_id:
            i += 1
            j += 1
        elif left[i].doc_id < right[j].doc_id:
            result.append(left[i])
            i += 1
        else:
            j += 1

    return result


def search_documents(query, index, documents, engine="merge"):
    terms = query.casefold().split()

    if not terms:
        return []

    if engine not in ("merge", "set"):
        raise ValueError("Engine must be 'merge' or 'set'")

    if len(terms) == 1:
        return [p.doc_id for p in index.get(terms[0], [])]

    if len(terms) == 2:
        first, second = terms
        operator = "and"
    elif len(terms) == 3:
        first, operator, second = terms
    else:
        raise ValueError("Use two terms with optional AND, OR or NOT")

    left = index.get(first, [])
    right = index.get(second, [])

    if operator == "and":
        result = merge_and(left, right) if engine == "merge" else set_and(left, right)
    elif operator == "or":
        result = merge_or(left, right) if engine == "merge" else set_or(left, right)
    elif operator == "not":
        if engine == "merge":
            result = merge_difference(left, right)
        else:
            right_ids = {p.doc_id for p in right}
            return [p.doc_id for p in left if p.doc_id not in right_ids]
    else:
        raise ValueError("Supported operators: AND, OR, NOT")

    return [p.doc_id for p in result]


def main():
    parser = argparse.ArgumentParser(description="Search an inverted index")
    parser.add_argument("index_file", type=Path)
    parser.add_argument("query")
    parser.add_argument("--engine", choices=["merge", "set"], default="merge")
    args = parser.parse_args()

    tracemalloc.start()
    start = time.perf_counter()

    index, documents = load_index(args.index_file)
    results = search_documents(args.query, index, documents, args.engine)

    elapsed = time.perf_counter() - start
    _, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(f"Query: {args.query}")
    print(f"Engine: {args.engine}")
    print(f"Results: {len(results)}")
    for doc_id in results[:10]:
        print(doc_id)

    print(f"Search time: {elapsed:.4f} seconds")
    print(f"Peak memory: {peak_memory / 1024 / 1024:.2f} MB")


if __name__ == "__main__":
    main()
