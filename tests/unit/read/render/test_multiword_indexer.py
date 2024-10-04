"""
get_string_indexes tests.
"""

import pytest
from lute.read.render.multiword_indexer import MultiwordTermIndexer

zws = "\u200B"  # zero-width space


@pytest.mark.parametrize(
    "name,terms,tokens,expected",
    [
        ("empty", [], ["a"], []),
        ("no terms", [], ["a"], []),
        ("no tokens", ["a"], [], []),
        ("no match", ["x"], ["a"], []),
        ("single match", ["a"], ["a"], [("a", 0)]),
        ("single match 2", ["a"], ["b", "a"], [("a", 1)]),
        ("same term twice", ["a"], ["b", "a", "c", "a"], [("a", 1), ("a", 3)]),
        (
            "multiple terms",
            ["a", "b"],
            ["b", "a", "c", "a"],
            [("b", 0), ("a", 1), ("a", 3)],
        ),
        ("multi-word term", [f"a{zws}b"], ["b", "a", "b", "a"], [(f"a{zws}b", 1)]),
        (
            "repeated m-word term",
            [f"a{zws}a"],
            ["a", "a", "a", "b"],
            [(f"a{zws}a", 0), (f"a{zws}a", 1)],
        ),
        ("bound check term at end", ["a"], ["b", "c", "a"], [("a", 2)]),
    ],
)
def test_scenario(name, terms, tokens, expected):
    "Test scenario."
    mw = MultiwordTermIndexer()
    for t in terms:
        mw.add(t)
    results = list(mw.search_all(tokens))
    assert len(results) == len(expected), name
    assert results == expected, name


def test_can_search_multiple_times_with_different_tokens():
    "Single match, returns token index."
    mw = MultiwordTermIndexer()
    mw.add("a")
    results = list(mw.search_all(["a", "b"]))
    assert len(results) == 1, "one match"
    assert results[0] == ("a", 0)

    results = list(mw.search_all(["b", "a"]))
    assert len(results) == 1, "one match"
    assert results[0] == ("a", 1)
