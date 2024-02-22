"""
Book tests.
"""

import textwrap
from lute.models.book import Book


def test_create_book(english):
    """
    When a book is created with given content, the content
    is split into separate Text objects.
    """
    fulltext = "Here is a dog. And a cat."
    scenario(english, fulltext, 5, ["Here is a dog.[4]", "And a cat.[3]"])
    scenario(english, fulltext, 500, ["Here is a dog. And a cat.[7]"])
    scenario(
        english,
        fulltext + " And a thing.",
        8,
        ["Here is a dog. And a cat.[7]", "And a thing.[3]"],
    )
    scenario(
        english,
        "Here is a dog.\nAnd a cat.",
        500,
        ["Here is a dog.\nAnd a cat.[7]"],
    )
    scenario(
        english,
        "Here is a dog.\n\n\nAnd a cat.",
        500,
        ["Here is a dog.\n\n\nAnd a cat.[7]"],
    )


def test_create_book_page_breaks(english):
    "--- on its own line means a page break."
    fulltext = textwrap.dedent(
        """\
      Here is a dog.
      And a cat.
    """
    )
    scenario(english, fulltext, 500, ["Here is a dog.\nAnd a cat.[7]"])

    fulltext = textwrap.dedent(
        """\
      Here is a dog.
      ---
      And a cat.
    """
    )
    scenario(english, fulltext, 500, ["Here is a dog.[4]", "And a cat.[3]"])

    fulltext = textwrap.dedent(
        """\
      Here is a dog.
      ---
      ---
      ---
      ---
      And a cat.
      ---
      ---
    """
    )
    scenario(english, fulltext, 500, ["Here is a dog.[4]", "And a cat.[3]"])


def scenario(english, fulltext, maxwords, expected):
    """
    Check scenarios.
    """
    b = Book.create_book("hi", english, fulltext, maxwords)

    actuals = [f"{t.text}[{t.word_count}]" for t in b.texts]
    print(actuals)
    assert "/".join(actuals) == "/".join(expected), f"scen {maxwords}, {fulltext}"
