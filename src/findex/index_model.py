from collections.abc import Mapping
from contextlib import contextmanager
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
import pickle


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


class Index(Mapping):
    __hash__ = object.__hash__
    __eq__ = object.__eq__

    def __init__(self, postings, documents):
        self._postings = postings
        self.documents = documents

    def __getitem__(self, term):
        return self._postings[term]

    def __iter__(self):
        return iter(self._postings)

    def __len__(self):
        return len(self._postings)

    def __contains__(self, term):
        return term in self._postings

    def __repr__(self):
        return f"Index(terms={len(self)}, docs={self.num_docs})"

    @property
    def num_docs(self):
        return len(self.documents)

    @cached_property
    def avg_doc_length(self):
        if not self.documents:
            return 0

        return sum(
            document.length for document in self.documents.values()
        ) / self.num_docs

    def doc_length(self, doc_id):
        return self.documents[doc_id].length

    def df(self, term):
        return len(self._postings.get(term, []))


@contextmanager
def open_index(path):
    with Path(path).open("rb") as file:
        index = pickle.load(file)
        yield index
