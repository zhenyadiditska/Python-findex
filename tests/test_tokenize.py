
from findex.tokenize import tokenize


def test_lowercase():
    assert list(tokenize("PYTHON JavaScript")) == ["python", "javascript"]


def test_punctuation():
    assert list(tokenize("Hello, world!")) == ["hello", "world"]


def test_numbers():
    assert list(tokenize("Python3 version 2026")) == ["python3", "version", "2026"]


def test_hyphen():
    assert list(tokenize("front-end web-development")) == [
        "front-end", "web-development"
    ]


def test_apostrophe():
    assert list(tokenize("don't user’s")) == ["don't", "user’s"]


def test_underscore():
    assert list(tokenize("web_dev")) == ["web", "dev"]


def test_unicode():
    assert list(tokenize("CAFÉ café")) == ["café", "café"]


def test_generator():
    result = tokenize("Python is great")
    assert iter(result) is result
    assert list(result) == ["python", "is", "great"]
