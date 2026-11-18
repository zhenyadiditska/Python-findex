from findex.index_model import open_index
from findex.search import rank_documents
from findex.scoring import TfIdf, BM25


queries = {
    "python": {
        "relevant": {
            "using/windows.txt",
            "whatsnew/3.14.txt",
            "whatsnew/index.txt",
            "faq/general.txt",
            "library/faulthandler.txt",
            "using/mac.txt",
            "extending/embedding.txt",
            "changelog.txt",
        }
    },
    "django": {
        "relevant": {
            "django/ref/class-based-views/flattened-index.txt",
            "django/releases/security.txt",
            "django/releases/1.8.txt",
            "django/releases/1.7.txt",
            "django/internals/deprecation.txt",
            "django/ref/class-based-views/generic-date-based.txt",
        }
    },
    "async": {
        "relevant": {
            "django/topics/async.txt",
            "asyncio-task.txt",
            "asyncio-eventloop.txt",
            "asyncio-dev.txt",
            "asyncio-sync.txt",
            "asyncio-stream.txt",
            "changelog.txt",
        }
    },
    "database": {
        "relevant": {
            "django/ref/models/querysets.txt",
            "django/topics/db/multi-db.txt",
            "django/ref/databases.txt",
            "django/ref/django-admin.txt",
            "sqlite3.txt",
            "library/dbm.txt",
            "django/topics/testing/overview.txt",
            "django/ref/migration-operations.txt",
        }
    },
    "security": {
        "relevant": {
            "django/internals/security.txt",
            "django/releases/security.txt",
            "django/ref/checks.txt",
            "library/security_warnings.txt",
            "django/topics/security.txt",
            "django/releases/5.2.11.txt",
            "django/releases/4.2.28.txt",
        }
    },
    "testing": {
        "relevant": {
            "django/topics/testing/tools.txt",
            "unittest.txt",
            "django/intro/tutorial05.txt",
            "library/test.txt",
            "django/topics/testing/index.txt",
            "django/topics/testing/advanced.txt",
        }
    },
    "template": {
        "relevant": {
            "django/ref/templates/api.txt",
            "django/topics/templates.txt",
            "django/howto/custom-template-tags.txt",
            "django/ref/templates/language.txt",
            "django/releases/1.8.txt",
            "library/string.templatelib.txt",
            "django/howto/custom-template-backend.txt",
            "django/ref/template-response.txt",
        }
    },
    "request": {
        "relevant": {
            "urllib.request.txt",
            "django/ref/request-response.txt",
            "howto/urllib2.txt",
            "django/topics/http/file-uploads.txt",
            "socketserver.txt",
            "django/topics/http/middleware.txt",
        }
    },
    "class AND method": {
        "relevant": {
            "reference/datamodel.txt",
            "django/ref/contrib/admin/index.txt",
            "django/ref/models/fields.txt",
            "library/typing.txt",
            "django/ref/contrib/auth.txt",
            "django/topics/class-based-views/intro.txt",
            "django/ref/class-based-views/mixins-editing.txt",
            "library/collections.abc.txt",
            "library/abc.txt",
        }
    },
    '"event loop"': {
        "relevant": {
            "asyncio-eventloop.txt",
            "asyncio-task.txt",
            "asyncio-llapi-index.txt",
            "conceptual-overview-of-asyncio.txt",
            "asyncio-policy.txt",
            "asyncio-runner.txt",
        }
    },
}


def precision_at_5(results, relevant):
    found = sum(
        1
        for result in results[:5]
        if any(
            result.doc_id == item
            or result.doc_id.endswith("/" + item)
            for item in relevant
        )
    )
    return found / 5


def main():
    with open_index("index.bin") as index:
        total_tfidf = 0
        total_bm25 = 0

        print("Оцінювання Precision@5")
        print("Кількість документів:", index.num_docs)

        for query, data in queries.items():
            relevant = data["relevant"]

            tfidf_results = rank_documents(
                query, index, TfIdf(), top_k=5
            )

            bm25_results = rank_documents(
                query, index, BM25(), top_k=5
            )

            tfidf_score = precision_at_5(
                tfidf_results, relevant
            )
            bm25_score = precision_at_5(
                bm25_results, relevant
            )

            total_tfidf += tfidf_score
            total_bm25 += bm25_score

            print("\n" + "=" * 55)
            print("Запит:", query)

            print("\nTF-IDF:")
            for result in tfidf_results:
                print(f"{result.score:.4f} - {result.doc_id}")
            print(f"Precision@5: {tfidf_score:.2f}")

            print("\nBM25:")
            for result in bm25_results:
                print(f"{result.score:.4f} - {result.doc_id}")
            print(f"Precision@5: {bm25_score:.2f}")

        count = len(queries)

        print("\n" + "=" * 55)
        print("СЕРЕДНІЙ РЕЗУЛЬТАТ")
        print("TF-IDF:", round(total_tfidf / count, 3))
        print("BM25:", round(total_bm25 / count, 3))


if __name__ == "__main__":
    main()
