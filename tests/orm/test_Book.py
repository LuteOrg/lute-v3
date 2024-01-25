"""
Book mapping checks.
"""

from datetime import datetime
import pytest
from lute.models.book import Book, BookTag
from lute.book.stats import BookStats
from lute.db import db
from tests.dbasserts import assert_sql_result, assert_record_count_equals


@pytest.fixture(name="simple_book")
def fixture_simple_book(english):
    "Single page book with some associated objects."
    b = Book.create_book("hi", english, "some text")
    b.texts[0].read_date = datetime.now()
    bt = BookTag.make_book_tag("hola")
    b.book_tags.append(bt)
    return b


def test_save_book(empty_db, simple_book):
    """
    Check book mappings.
    """
    b = simple_book
    db.session.add(b)
    db.session.commit()

    sql = "select BkID, BkTitle, BkLgID from books"
    assert_sql_result(sql, ["1; hi; 1"], "book")

    sql = "select TxID, TxBkID, TxText from texts"
    assert_sql_result(sql, ["1; 1; some text"], "texts")

    sql = "select * from sentences"
    assert_sql_result(sql, ["1; 1; 1; /some/ /text/"], "sentences")

    sql = "select * from booktags"
    assert_sql_result(sql, ["1; 1"], "booktags")

    sql = "select * from tags2"
    assert_sql_result(sql, ["1; hola; "], "tags2")


def test_delete_book(empty_db, simple_book):
    """
    Most tables should clear out after delete.
    """
    b = simple_book
    db.session.add(b)
    db.session.commit()

    db.session.delete(b)
    db.session.commit()

    for t in ["books", "texts", "sentences", "booktags"]:
        assert_record_count_equals(t, 0, f"{t} deleted")

    sql = "select * from tags2"
    assert_sql_result(sql, ["1; hola; "], "tags2 remain")


def test_save_and_delete_created_book(english):
    """
    Verify book orm mappings.
    """
    content = "Some text here. Some more text"
    b = Book.create_book("test", english, content, 3)
    db.session.add(b)
    db.session.commit()
    sql = f"select TxOrder, TxText from texts where TxBkID = {b.id}"
    expected = ["1; Some text here.", "2; Some more text"]
    assert_sql_result(sql, expected, "texts")

    db.session.delete(b)
    db.session.commit()
    assert_sql_result(sql, [], "texts deleted")


def test_load_book_loads_lang(empty_db, simple_book):
    """
    Check book mappings.
    """
    b = simple_book
    db.session.add(b)
    db.session.commit()

    findbook = db.session.query(Book).filter(Book.title == "hi").first()
    assert findbook.title == "hi", "title"
    assert findbook.language.name == "English", "check lang"

    for b in db.session.query(Book).all():
        assert b.language is not None, "have lang object"

    books_to_update = (
        db.session.query(Book)
        .filter(~Book.id.in_(db.session.query(BookStats.BkID)))
        .all()
    )
    for b in books_to_update:
        assert b.language is not None, "have lang object"
