import argparse
import time
import tracemalloc
from pathlib import Path
from heapq import nlargest

from findex.index_model import open_index
from findex.scoring import TfIdf, BM25, SearchResult
from findex.decorators import timed
from findex.query import Term, Phrase, And, Or, Not, parse_query
from findex.snippets import make_snippet
from findex.cache import cached_query


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


def search_documents(query, index, documents=None, engine="merge"):
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


def collect_terms(node, negated=False):
    if isinstance(node, Term):
        return [] if negated else [node.value.casefold()]

    if isinstance(node, Phrase):
        return [] if negated else node.value.casefold().split()

    if isinstance(node, Not):
        return collect_terms(node.node, not negated)

    if isinstance(node, (And, Or)):
        return (
            collect_terms(node.left, negated)
            + collect_terms(node.right, negated)
        )

    return []


@timed
def rank_documents(query, index, scorer=None, top_k=10):
    if scorer is None:
        scorer = TfIdf()

    tree = parse_query(query)
    matching_documents = set(cached_query(query, index))

    if not matching_documents:
        return []

    terms = collect_terms(tree)
    scores = {doc_id: 0.0 for doc_id in matching_documents}

    for term in terms:
        for posting in index.get(term, []):
            if posting.doc_id in matching_documents:
                score = scorer.score(term, posting, index)
                scores[posting.doc_id] += score

    results = [
        SearchResult(
            doc_id=doc_id,
            score=score,
            title=index.documents[doc_id].path.split("/")[-1]
        )
        for doc_id, score in scores.items()
    ]

    return nlargest(top_k, results)


def main():
    parser = argparse.ArgumentParser(description="Search an inverted index")
    parser.add_argument("index_file", type=Path)
    parser.add_argument("query")
    parser.add_argument("--engine", choices=["merge", "set"], default="merge")
    parser.add_argument("--scorer", choices=["tfidf", "bm25"], default="tfidf")
    parser.add_argument("--top-k", type=int, default=10)
    args = parser.parse_args()

    tracemalloc.start()
    start = time.perf_counter()

    with open_index(args.index_file) as index:
        scorer = BM25() if args.scorer == "bm25" else TfIdf()

        results = rank_documents(
            args.query,
            index,
            scorer=scorer,
            top_k=args.top_k
        )

        terms = collect_terms(parse_query(args.query))

        print(f"Query: {args.query}")
        print(f"Scorer: {args.scorer}")
        print(f"Results: {len(results)}")

        for result in results:
            document = index.documents[result.doc_id]

            snippet = make_snippet(
                document.path,
                terms,
                window=80
            )

            print(f"\n{result.score:.4f} | {result.doc_id}")
            print(snippet)

    elapsed = time.perf_counter() - start
    _, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(f"\nSearch time: {elapsed:.4f} seconds")
    print(f"Peak memory: {peak_memory / 1024 / 1024:.2f} MB")


if __name__ == "__main__":
    main()
