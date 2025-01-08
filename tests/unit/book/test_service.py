"""
Book service tests.
"""

import pytest
from lute.book.service import Service


@pytest.mark.parametrize(
    "fulltext,maxwords,expected",
    [
        ("Test.", 200, ["Test."]),
        ("Here is a dog. And a cat.", 5, ["Here is a dog.", "And a cat."]),
        ("Here is a dog. And a cat.", 500, ["Here is a dog. And a cat."]),
        ("Here is a dog.\nAnd a cat.", 500, ["Here is a dog.\nAnd a cat."]),
        ("\nHere is a dog.\n\nAnd a cat.\n", 500, ["Here is a dog.\n\nAnd a cat."]),
        ("Here is a dog.\n---\nAnd a cat.", 200, ["Here is a dog.", "And a cat."]),
        ("Here is a dog. A cat. A thing.", 7, ["Here is a dog. A cat.", "A thing."]),
        ("Dog.\n---\n---\nCat.\n---\n", 5, ["Dog.", "Cat."]),
    ],
)
def test_split_sentences_scenario(fulltext, maxwords, expected, english):
    "Check scenarios."
    svc = Service()
    actuals = svc.split_by_sentences(english, fulltext, maxwords)
    assert "/".join(actuals) == "/".join(expected), f"scen {maxwords}, {fulltext}"


def test_create_book(english):
    "Sanity check only."
    svc = Service()
    b = svc.create_book("hi", english, "Hello there.", 200)
    assert b.page_count == 1
    assert b.texts[0].text == "Hello there."
