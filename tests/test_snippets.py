from findex.snippets import make_snippet


def test_make_snippet_highlights_term(tmp_path):
    file = tmp_path / "document.txt"
    file.write_text("Python is a programming language.", encoding="utf-8")

    result = make_snippet(file, ["python"])

    assert "**Python**" in result


def test_make_snippet_returns_empty_for_missing_file():
    result = make_snippet("missing.txt", ["python"])

    assert result == ""


def test_make_snippet_without_terms(tmp_path):
    file = tmp_path / "document.txt"
    file.write_text("Some example text.", encoding="utf-8")

    result = make_snippet(file, [])

    assert result == "Some example text."
