from findex.query import (
    parse_query,
    Term,
    Phrase,
    And,
    Or,
    Not,
)
from findex.index_model import Index, Posting, DocMeta


def create_test_index():
    documents = {
        "doc1": DocMeta("doc1", "doc1.txt", 3),
        "doc2": DocMeta("doc2", "doc2.txt", 3),
        "doc3": DocMeta("doc3", "doc3.txt", 2),
    }

    postings = {
        "python": [
            Posting("doc1", 1, (0,)),
            Posting("doc2", 1, (0,)),
        ],
        "django": [
            Posting("doc1", 1, (1,)),
        ],
        "async": [
            Posting("doc1", 1, (2,)),
            Posting("doc3", 1, (1,)),
        ],
        "java": [
            Posting("doc2", 1, (2,)),
        ],
        "event": [
            Posting("doc1", 1, (0,)),
            Posting("doc2", 1, (0,)),
        ],
        "loop": [
            Posting("doc1", 1, (1,)),
            Posting("doc2", 1, (2,)),
        ],
    }

    return Index(postings, documents)


def test_parse_term():
    assert parse_query("python") == Term("python")


def test_parse_and():
    assert parse_query("python AND django") == And(
        Term("python"),
        Term("django"),
    )


def test_parse_or():
    assert parse_query("async OR await") == Or(
        Term("async"),
        Term("await"),
    )


def test_parse_not():
    assert parse_query("NOT java") == Not(Term("java"))


def test_parse_complex_query():
    expected = And(
        And(
            Term("python"),
            Or(Term("async"), Term("await")),
        ),
        Not(Term("java")),
    )

    assert parse_query(
        "python AND (async OR await) NOT java"
    ) == expected


def test_parse_phrase():
    assert parse_query('"event loop"') == Phrase("event loop")


def test_evaluate_and():
    index = create_test_index()

    result = parse_query("python AND django").evaluate(index)

    assert result == {"doc1"}


def test_evaluate_or():
    index = create_test_index()

    result = parse_query("django OR async").evaluate(index)

    assert result == {"doc1", "doc3"}


def test_evaluate_not():
    index = create_test_index()

    result = parse_query("NOT java").evaluate(index)

    assert result == {"doc1", "doc3"}


def test_evaluate_phrase():
    index = create_test_index()

    result = parse_query('"event loop"').evaluate(index)

    assert result == {"doc1"}


def test_empty_query():
    import pytest

    with pytest.raises(ValueError):
        parse_query("")


def test_parse_implicit_and():
    expected = Or(
        Term("a"),
        And(Term("b"), Term("c")),
    )

    assert parse_query("a OR b c") == expected
