import gc
import tracemalloc
from array import array
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from findex.index import load_index


@dataclass(frozen=True)
class PostingNormal:
    doc_id: int
    frequency: int


@dataclass(frozen=True, slots=True)
class PostingSlots:
    doc_id: int
    frequency: int


def measure_memory(
    name: str,
    create_data: Callable[[], object],
) -> None:
    tracemalloc.start()

    data = create_data()

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(f"{name}:")
    print(f"  Current memory: {current / 1024 / 1024:.2f} MB")
    print(f"  Peak memory: {peak / 1024 / 1024:.2f} MB")

    del data
    gc.collect()


def main() -> None:
    index = load_index(Path("index.bin"))
    documents = index.documents

    doc_ids = {
        doc_id: number
        for number, doc_id in enumerate(documents)
    }

    postings: list[tuple[int, int]] = [
        (doc_ids[posting.doc_id], posting.frequency)
        for posting_list in index.postings.values()
        for posting in posting_list
    ]

    print(f"Number of postings: {len(postings)}\n")

    measure_memory(
        "Normal dataclass",
        lambda: [
            PostingNormal(doc_id, frequency)
            for doc_id, frequency in postings
        ],
    )

    measure_memory(
        "Dataclass with slots",
        lambda: [
            PostingSlots(doc_id, frequency)
            for doc_id, frequency in postings
        ],
    )

    def create_array() -> array[int]:
        data: array[int] = array("I")

        for doc_id, frequency in postings:
            data.append(doc_id)
            data.append(frequency)

        return data

    measure_memory("Array of unsigned integers", create_array)


if __name__ == "__main__":
    main()