
from findex.index import Posting
from findex.search import search_documents


def create_test_index():
    index = {
        "python": [
            Posting("doc1", 2),
            Posting("doc2", 1),
            Posting("doc4", 3),
        ],
        "django": [
            Posting("doc2", 2),
            Posting("doc3", 1),
        ],
    }

    documents = {
        "doc1": None,
        "doc2": None,
        "doc3": None,
        "doc4": None,
    }

    return index, documents


def test_and_merge():
    index, documents = create_test_index()
    result = search_documents("python AND django", index, documents, "merge")
    assert result == ["doc2"]


def test_and_set():
    index, documents = create_test_index()
    result = search_documents("python AND django", index, documents, "set")
    assert result == ["doc2"]


def test_or_merge():
    index, documents = create_test_index()
    result = search_documents("python OR django", index, documents, "merge")
    assert result == ["doc1", "doc2", "doc3", "doc4"]


def test_or_set():
    index, documents = create_test_index()
    result = search_documents("python OR django", index, documents, "set")
    assert result == ["doc1", "doc2", "doc3", "doc4"]


def test_not_merge():
    index, documents = create_test_index()
    result = search_documents("python NOT django", index, documents, "merge")
    assert result == ["doc1", "doc4"]


def test_not_set():
    index, documents = create_test_index()
    result = search_documents("python NOT django", index, documents, "set")
    assert result == ["doc1", "doc4"]
