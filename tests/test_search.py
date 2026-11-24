
from findex.index_model import DocMeta, Index, Posting
from findex.search import search_documents


def create_test_index() -> Index:
    postings = {
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
        "doc1": DocMeta("doc1", "doc1.txt", 3),
        "doc2": DocMeta("doc2", "doc2.txt", 3),
        "doc3": DocMeta("doc3", "doc3.txt", 2),
        "doc4": DocMeta("doc4", "doc4.txt", 4),
    }

    return Index(postings, documents)


def test_and_merge() -> None:
    index = create_test_index()
    result = search_documents("python AND django", index, engine="merge")

    assert result == ["doc2"]


def test_and_set() -> None:
    index = create_test_index()
    result = search_documents("python AND django", index, engine="set")

    assert result == ["doc2"]


def test_or_merge() -> None:
    index = create_test_index()
    result = search_documents("python OR django", index, engine="merge")

    assert result == ["doc1", "doc2", "doc3", "doc4"]


def test_or_set() -> None:
    index = create_test_index()
    result = search_documents("python OR django", index, engine="set")

    assert result == ["doc1", "doc2", "doc3", "doc4"]


def test_not_merge() -> None:
    index = create_test_index()
    result = search_documents("python NOT django", index, engine="merge")

    assert result == ["doc1", "doc4"]


def test_not_set() -> None:
    index = create_test_index()
    result = search_documents("python NOT django", index, engine="set")

    assert result == ["doc1", "doc4"]
