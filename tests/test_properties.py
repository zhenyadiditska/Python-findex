from pathlib import Path
from tempfile import TemporaryDirectory

from hypothesis import given
from hypothesis import strategies as st
from hypothesis.strategies import DrawFn

from findex.index import load_index, save_index
from findex.index_model import DocMeta, Index, Posting
from findex.search import merge_and, merge_difference, merge_or


@st.composite
def indexes(draw: DrawFn) -> Index:
    doc_ids: list[int] = draw(
        st.lists(
            st.integers(min_value=1, max_value=1000),
            unique=True,
            max_size=20,
        )
    )

    sorted_ids = sorted(str(doc_id) for doc_id in doc_ids)

    documents = {
        doc_id: DocMeta(
            doc_id=doc_id,
            path=f"{doc_id}.txt",
            length=3,
        )
        for doc_id in sorted_ids
    }

    postings = {
        "python": [
            Posting(
                doc_id=doc_id,
                frequency=1,
                positions=(0,),
            )
            for doc_id in sorted_ids
        ]
    }

    return Index(postings, documents)


@st.composite
def posting_lists(draw: DrawFn) -> tuple[list[Posting], list[Posting]]:
    left_ids: list[int] = draw(
        st.lists(
            st.integers(min_value=1, max_value=1000),
            unique=True,
            max_size=20,
        )
    )
    right_ids: list[int] = draw(
        st.lists(
            st.integers(min_value=1, max_value=1000),
            unique=True,
            max_size=20,
        )
    )

    left = [
        Posting(doc_id, 1)
        for doc_id in sorted(str(value) for value in left_ids)
    ]
    right = [
        Posting(doc_id, 1)
        for doc_id in sorted(str(value) for value in right_ids)
    ]

    return left, right


@given(index=indexes())
def test_save_load_property(index: Index) -> None:
    with TemporaryDirectory() as directory:
        file_path = Path(directory) / "index.bin"

        save_index(index, file_path)
        loaded = load_index(file_path)

        assert loaded.postings == index.postings
        assert loaded.documents == index.documents


@given(lists=posting_lists())
def test_merge_results_are_sorted(
    lists: tuple[list[Posting], list[Posting]],
) -> None:
    left, right = lists

    results = [
        merge_and(left, right),
        merge_or(left, right),
        merge_difference(left, right),
    ]

    for result in results:
        doc_ids = [posting.doc_id for posting in result]
        assert doc_ids == sorted(doc_ids)


@given(lists=posting_lists())
def test_merge_matches_set_operations(
    lists: tuple[list[Posting], list[Posting]],
) -> None:
    left, right = lists

    left_ids = {posting.doc_id for posting in left}
    right_ids = {posting.doc_id for posting in right}

    assert {
        posting.doc_id for posting in merge_and(left, right)
    } == left_ids & right_ids

    assert {
        posting.doc_id for posting in merge_or(left, right)
    } == left_ids | right_ids

    assert {
        posting.doc_id for posting in merge_difference(left, right)
    } == left_ids - right_ids