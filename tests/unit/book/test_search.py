"""
Book search tests.
"""

from lute.db import db
from lute.book.service import Service
from tests.utils import make_book


def test_search_books_for_term(app_context, spanish):
    """
    Verify search_books_for_term locates the correct book and extracts
    containing phrases with page numbers.
    """
    svc = Service()

    # Create book 1 (page 1 and page 2)
    b1 = make_book(
        "Spanish Adventure",
        ["Me gusta comer manzanas.", "Tengo un perro grande."],
        spanish,
    )
    for text_obj in b1.texts:
        text_obj.load_sentences()
    db.session.add(b1)

    # Create book 2 (page 1 and page 2)
    b2 = make_book(
        "Spanish Cooking",
        ["Las manzanas son deliciosas.", "No me gusta el pescado."],
        spanish,
    )
    for text_obj in b2.texts:
        text_obj.load_sentences()
    db.session.add(b2)

    db.session.commit()

    # Search for term "manzanas"
    results = svc.search_books_for_term("manzanas", db.session)

    assert len(results) == 2

    # Map results by title for easy assert
    res_map = {r["title"]: r for r in results}

    assert "Spanish Adventure" in res_map
    assert res_map["Spanish Adventure"]["phrases"] == [
        {"text": "Me gusta comer manzanas.", "page": 1}
    ]

    assert "Spanish Cooking" in res_map
    assert res_map["Spanish Cooking"]["phrases"] == [
        {"text": "Las manzanas son deliciosas.", "page": 1}
    ]

    # Search for term "perro"
    results2 = svc.search_books_for_term("perro", db.session)
    assert len(results2) == 1
    assert results2[0]["title"] == "Spanish Adventure"
    assert results2[0]["phrases"] == [{"text": "Tengo un perro grande.", "page": 2}]

    # Search for term "gusta" (should match both books)
    results3 = svc.search_books_for_term("gusta", db.session)
    assert len(results3) == 2
    res_map3 = {r["title"]: r for r in results3}
    assert {"text": "Me gusta comer manzanas.", "page": 1} in res_map3[
        "Spanish Adventure"
    ]["phrases"]
    assert {"text": "No me gusta el pescado.", "page": 2} in res_map3[
        "Spanish Cooking"
    ]["phrases"]

    # Search for partial term "manzan"
    results4 = svc.search_books_for_term("manzan", db.session)
    assert len(results4) == 2
    res_map4 = {r["title"]: r for r in results4}
    assert {"text": "Me gusta comer manzanas.", "page": 1} in res_map4[
        "Spanish Adventure"
    ]["phrases"]
    assert {
        "text": "Las manzanas son deliciosas.",
        "page": 1,
    } in res_map4[
        "Spanish Cooking"
    ]["phrases"]


def test_search_books_for_term_long_content(app_context, spanish):
    """
    Verify search_books_for_term extracts exactly a 200-character snippet with the term centered.
    """
    svc = Service()

    # 150 chars padding + "manzanas" (8 chars) + 150 chars padding
    left_padding = "a " * 75
    right_padding = " b" * 75
    long_text = f"{left_padding}manzanas{right_padding}"

    b = make_book("Long Book", long_text, spanish)
    for text_obj in b.texts:
        text_obj.load_sentences()
    db.session.add(b)
    db.session.commit()

    results = svc.search_books_for_term("manzanas", db.session)
    assert len(results) == 1
    phrase_obj = results[0]["phrases"][0]
    phrase = phrase_obj["text"]
    page = phrase_obj["page"]

    # The snippet must have ellipses on both sides because it is truncated
    assert phrase.startswith("...")
    assert phrase.endswith("...")

    # Stripping ellipses, the length of the actual extracted snippet must be exactly 200 characters
    clean_snippet = phrase[3:-3]
    assert len(clean_snippet) == 200

    # The term "manzanas" should be in the middle of the clean snippet
    # 200 total chars - 8 chars ("manzanas") = 192 padding chars total.
    # Centered means 96 characters from left_padding, and 96 characters from right_padding.
    expected_snippet = left_padding[54:] + "manzanas" + right_padding[:96]
    assert clean_snippet == expected_snippet
    assert page == 1
