from dataclasses import dataclass
from array import array
from pathlib import Path
import tracemalloc
import gc

from findex.index import load_index


@dataclass(frozen=True)
class PostingNormal:
    doc_id: int
    frequency: int


@dataclass(frozen=True, slots=True)
class PostingSlots:
    doc_id: int
    frequency: int


def measure_memory(name, create_data):
    tracemalloc.start()
    data = create_data()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(f"{name}:")
    print(f"  Current memory: {current / 1024 / 1024:.2f} MB")
    print(f"  Peak memory: {peak / 1024 / 1024:.2f} MB")

    del data
    gc.collect()


def main():
    index, documents = load_index(Path("index.bin"))

    doc_ids = {
        doc_id: number
        for number, doc_id in enumerate(documents)
    }

    postings = [
        (doc_ids[posting.doc_id], posting.frequency)
        for posting_list in index.values()
        for posting in posting_list
    ]

    print(f"Number of postings: {len(postings)}\n")

    measure_memory(
        "Normal dataclass",
        lambda: [
            PostingNormal(doc_id, frequency)
            for doc_id, frequency in postings
        ]
    )

    measure_memory(
        "Dataclass with slots",
        lambda: [
            PostingSlots(doc_id, frequency)
            for doc_id, frequency in postings
        ]
    )

    def create_array():
        data = array("I")
        for doc_id, frequency in postings:
            data.append(doc_id)
            data.append(frequency)
        return data

    measure_memory("Array of unsigned integers", create_array)


if __name__ == "__main__":
    main()
