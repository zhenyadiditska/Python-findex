
import argparse
import tracemalloc
from collections import Counter
from pathlib import Path
from time import perf_counter

from findex.corpus import iter_documents
from findex.tokenize import tokenize


def analyze_corpus(data_dir: Path, limit: int | None = None):
    counter = Counter()
    document_count = 0
    total_tokens = 0

    tracemalloc.start()
    start_time = perf_counter()

    for document in iter_documents(data_dir):
        if limit is not None and document_count >= limit:
            break

        document_count += 1

        for token in tokenize(document.text):
            counter[token] += 1
            total_tokens += 1

    elapsed_time = perf_counter() - start_time
    current_memory, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print("\nCorpus statistics")
    print("-------------------------")
    print(f"Documents: {document_count}")
    print(f"Total tokens: {total_tokens}")
    print(f"Unique tokens: {len(counter)}")

    print("\nTop 50 terms:")
    for word, count in counter.most_common(50):
        print(f"{word}: {count}")

    print("\nPerformance")
    print("-------------------------")
    print(f"Time: {elapsed_time:.6f} seconds")
    print(f"Peak memory: {peak_memory / 1024:.2f} KB")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    analyze_corpus(Path("data"), args.limit)


if __name__ == "__main__":
    main()
