
import pickle
from collections.abc import Generator, Iterator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Posting:
    doc_id: str
    frequency: int
    positions: tuple[int, ...] = ()


@dataclass(frozen=True, slots=True)
class DocMeta:
    doc_id: str
    path: str
    length: int


class Index(Mapping[str, list[Posting]]):
    def __init__(
        self,
        postings: dict[str, list[Posting]],
        documents: dict[str, DocMeta],
    ) -> None:
        self.postings = postings
        self.documents = documents

    def __getitem__(self, term: str) -> list[Posting]:
        return self.postings[term]

    def __iter__(self) -> Iterator[str]:
        return iter(self.postings)

    def __len__(self) -> int:
        return len(self.postings)

    def __contains__(self, term: object) -> bool:
        return term in self.postings

    def __repr__(self) -> str:
        return (
            f"Index(terms={len(self)}, "
            f"documents={self.num_docs})"
        )

    def __eq__(self, other: object) -> bool:
        return self is other

    def __hash__(self) -> int:
        return object.__hash__(self)

    @property
    def num_docs(self) -> int:
        return len(self.documents)

    @cached_property
    def avg_doc_length(self) -> float:
        if not self.documents:
            return 0.0

        total_length = sum(
            document.length for document in self.documents.values()
        )
        return total_length / len(self.documents)

    def doc_length(self, doc_id: str) -> int:
        return self.documents[doc_id].length

    def df(self, term: str) -> int:
        return len(self.postings.get(term, []))


@contextmanager
def open_index(path: str | Path) -> Generator[Index]:
    with Path(path).open("rb") as file:
        index = pickle.load(file)

        if not isinstance(index, Index):
            raise TypeError("File does not contain a valid Index")

        yield index
