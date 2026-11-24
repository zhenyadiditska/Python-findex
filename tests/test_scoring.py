
from findex.index_model import Index, Posting
from findex.scoring import BM25, TfIdf


def test_tfidf_rare_term_scores_higher(sample_index: Index) -> None:
    scorer = TfIdf()

    rare_score = scorer.score("django", Posting("doc1", 1), sample_index)
    common_score = scorer.score("python", Posting("doc1", 1), sample_index)

    assert rare_score > common_score


def test_bm25_rare_term_scores_higher(sample_index: Index) -> None:
    scorer = BM25()

    rare_score = scorer.score("django", Posting("doc1", 1), sample_index)
    common_score = scorer.score("python", Posting("doc1", 1), sample_index)

    assert rare_score > common_score


def test_bm25_term_frequency_saturation(sample_index: Index) -> None:
    scorer = BM25()

    score_1 = scorer.score("python", Posting("doc1", 1), sample_index)
    score_2 = scorer.score("python", Posting("doc1", 2), sample_index)
    score_19 = scorer.score("python", Posting("doc1", 19), sample_index)
    score_20 = scorer.score("python", Posting("doc1", 20), sample_index)

    assert score_20 > score_19
    assert score_20 - score_19 < score_2 - score_1


def test_bm25_shorter_document_scores_higher(sample_index: Index) -> None:
    scorer = BM25()

    short_score = scorer.score("python", Posting("doc1", 1), sample_index)
    long_score = scorer.score("python", Posting("doc4", 1), sample_index)

    assert short_score > long_score


def test_tfidf_unknown_term_returns_zero(sample_index: Index) -> None:
    scorer = TfIdf()

    score = scorer.score("unknown", Posting("doc1", 1), sample_index)

    assert score == 0.0


def test_bm25_unknown_term_returns_zero(sample_index: Index) -> None:
    scorer = BM25()

    score = scorer.score("unknown", Posting("doc1", 1), sample_index)

    assert score == 0.0
