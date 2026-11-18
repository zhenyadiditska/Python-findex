from dataclasses import dataclass, field
from math import log
from typing import Protocol

from findex.index_model import Index, Posting


@dataclass(order=True, frozen=True)
class SearchResult:
    doc_id: str = field(compare=False)
    score: float
    title: str = field(default="", compare=False)

    def __str__(self):
        return f"{self.score:.4f} - {self.title or self.doc_id}"


class Scorer(Protocol):
    def score(self, term: str, posting: Posting, index: Index) -> float:
        ...


class TfIdf:
    def score(self, term: str, posting: Posting, index: Index) -> float:
        tf = posting.frequency
        df = index.df(term)
        total_docs = index.num_docs

        if total_docs == 0 or df == 0:
            return 0.0

        idf = log((total_docs + 1) / (df + 1)) + 1
        return tf * idf


class BM25:
    def __init__(self, k1=1.5, b=0.75):
        self.k1 = k1
        self.b = b

    def score(self, term: str, posting: Posting, index: Index) -> float:
        tf = posting.frequency
        df = index.df(term)
        total_docs = index.num_docs

        if total_docs == 0 or df == 0:
            return 0.0

        idf = log(1 + (total_docs - df + 0.5) / (df + 0.5))
        doc_length = index.doc_length(posting.doc_id)
        avg_length = index.avg_doc_length

        if avg_length == 0:
            return 0.0

        numerator = tf * (self.k1 + 1)
        denominator = tf + self.k1 * (
            1 - self.b + self.b * doc_length / avg_length
        )

        return idf * numerator / denominator
