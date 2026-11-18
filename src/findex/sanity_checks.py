from findex.index_model import Posting, open_index
from findex.scoring import TfIdf, BM25


def check_rare_term(index):
    terms = [term for term in index if index.df(term) > 0]
    rare = min(terms, key=lambda term: index.df(term))
    common = max(terms, key=lambda term: index.df(term))

    doc_id = index[rare][0].doc_id

    rare_posting = Posting(doc_id, 1)
    common_posting = Posting(doc_id, 1)

    print("\n1. Рідкісний і поширений термін")
    print("Рідкісний термін:", rare, "| DF:", index.df(rare))
    print("Поширений термін:", common, "| DF:", index.df(common))

    for scorer in (TfIdf(), BM25()):
        rare_score = scorer.score(rare, rare_posting, index)
        common_score = scorer.score(common, common_posting, index)

        print(type(scorer).__name__)
        print("Оцінка рідкісного:", round(rare_score, 4))
        print("Оцінка поширеного:", round(common_score, 4))
        print("Рідкісний термін має вищу оцінку:",
              rare_score > common_score)


def check_bm25_repetition(index):
    term = max(index, key=lambda item: index.df(item))
    posting = index[term][0]
    scorer = BM25()

    score_1 = scorer.score(
        term, Posting(posting.doc_id, 1), index
    )
    score_19 = scorer.score(
        term, Posting(posting.doc_id, 19), index
    )
    score_20 = scorer.score(
        term, Posting(posting.doc_id, 20), index
    )

    print("\n2. Насичення BM25")
    print("Термін:", term)
    print("1 повторення:", round(score_1, 4))
    print("19 повторень:", round(score_19, 4))
    print("20 повторень:", round(score_20, 4))
    print("Приріст між 19 і 20:",
          round(score_20 - score_19, 6))


def check_document_length(index):
    best_pair = None
    best_ratio = 1

    for term, postings in index.items():
        single_matches = [
            posting for posting in postings
            if posting.frequency == 1
        ]

        if len(single_matches) < 2:
            continue

        ordered = sorted(
            single_matches,
            key=lambda posting: index.doc_length(posting.doc_id)
        )

        short = ordered[0]
        long = ordered[-1]

        short_length = index.doc_length(short.doc_id)
        long_length = index.doc_length(long.doc_id)

        if short_length == 0:
            continue

        ratio = long_length / short_length

        if ratio > best_ratio:
            best_ratio = ratio
            best_pair = (term, short, long)

    print("\n3. Вплив довжини документа в BM25")

    if best_pair is None:
        print("Не знайдено відповідної пари документів.")
        return

    term, short, long = best_pair
    scorer = BM25()

    short_score = scorer.score(term, short, index)
    long_score = scorer.score(term, long, index)

    print("Спільний термін:", term)
    print("Частота в обох документах:", 1)
    print("\nКороткий документ:", short.doc_id)
    print("Довжина:", index.doc_length(short.doc_id))
    print("Оцінка:", round(short_score, 4))
    print("\nДовгий документ:", long.doc_id)
    print("Довжина:", index.doc_length(long.doc_id))
    print("Оцінка:", round(long_score, 4))
    print("\nКороткий документ має вищу оцінку:",
          short_score > long_score)


def main():
    with open_index("index.bin") as index:
        print(index)
        check_rare_term(index)
        check_bm25_repetition(index)
        check_document_length(index)


if __name__ == "__main__":
    main()
