
import tracemalloc
from collections import Counter
from pathlib import Path
from time import perf_counter

from findex.corpus import iter_documents
from findex.tokenize import tokenize


def analyze_greedy(data_dir: Path):
    tracemalloc.start()
    start_time = perf_counter()

    documents = list(iter_documents(data_dir))

    all_tokens = []
    for document in documents:
        all_tokens.extend(list(tokenize(document.text)))

    counter = Counter(all_tokens)

    elapsed_time = perf_counter() - start_time
    _, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print("\nGreedy corpus statistics")
    print("-------------------------")
    print(f"Documents: {len(documents)}")
    print(f"Total tokens: {len(all_tokens)}")
    print(f"Unique tokens: {len(counter)}")

    print("\nTop 50 terms:")
    for word, count in counter.most_common(50):
        print(f"{word}: {count}")

    print("\nPerformance")
    print("-------------------------")
    print(f"Time: {elapsed_time:.6f} seconds")
    print(f"Peak memory: {peak_memory / 1024:.2f} KB")


if __name__ == "__main__":
    analyze_greedy(Path("data"))
