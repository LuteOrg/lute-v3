"""
Book tests.
"""

import textwrap
from lute.models.book import Book
from lute.db import db
from tests.dbasserts import assert_sql_result


# pylint: disable=too-many-arguments
def assert_add(book, pagenum, before, text, expected, msg=""):
    "Assert that adding results in expected table content."
    sql = f"""
    select TxText, TxOrder from Texts
    where TxBkID = {book.id}
    order by TxOrder"""

    t = None
    if before:
        t = book.add_page_before(pagenum)
    else:
        t = book.add_page_after(pagenum)
    t.text = text
    db.session.add(book)
    db.session.commit()
    assert_sql_result(sql, expected, msg)


def assert_remove(book, pagenum, expected, msg):
    "assert removed"
    sql = f"""
    select TxText, TxOrder from Texts
    where TxBkID = {book.id}
    order by TxOrder"""

    book.remove_page(pagenum)

    db.session.add(book)
    db.session.commit()
    assert_sql_result(sql, expected, msg)


def test_can_add_page(app_context, english):
    "Add page before and after."
    fulltext = textwrap.dedent(
        """\
      1
      ---
      2
      ---
      3
    """
    )
    b = Book.create_book("hi", english, fulltext)
    db.session.add(b)
    db.session.commit()

    sql = f"""
    select TxText, TxOrder from Texts
    where TxBkID = {b.id}
    order by TxOrder"""
    assert_sql_result(sql, ["1; 1", "2; 2", "3; 3"], "initial book")

    assert_add(b, 2, True, "B2", ["1; 1", "B2; 2", "2; 3", "3; 4"], "new")
    assert_add(b, 3, False, "A4", ["1; 1", "B2; 2", "2; 3", "A4; 4", "3; 5"], "new")


def test_add_page_before_first(app_context, english):
    "Add page before and after."
    b = Book.create_book("hi", english, "hi")
    db.session.add(b)
    db.session.commit()

    assert_add(b, 1, True, "B1", ["B1; 1", "hi; 2"], "new")
    assert_add(b, 0, True, "B0", ["B0; 1", "B1; 2", "hi; 3"], "0")
    assert_add(b, -100, True, "B-", ["B-; 1", "B0; 2", "B1; 3", "hi; 4"], "neg")
    assert_add(b, 100, True, "B+", ["B-; 1", "B0; 2", "B1; 3", "B+; 4", "hi; 5"], "big")


def test_add_page_after_last(app_context, english):
    "Add page after last."
    b = Book.create_book("hi", english, "hi")
    db.session.add(b)
    db.session.commit()

    assert_add(b, 1, False, "B1", ["hi; 1", "B1; 2"], "new")
    assert_add(b, 100, False, "B100", ["hi; 1", "B1; 2", "B100; 3"], "100")
    assert_add(b, -100, False, "Bneg", ["hi; 1", "Bneg; 2", "B1; 3", "B100; 4"], "neg")


def test_can_remove_page(app_context, english):
    "Remove pages before and after."
    fulltext = textwrap.dedent(
        """\
      1
      ---
      2
      ---
      3
    """
    )
    b = Book.create_book("hi", english, fulltext)
    db.session.add(b)
    db.session.commit()

    assert_remove(b, 2, ["1; 1", "3; 2"], "2nd page removed")
    assert_remove(b, 12, ["1; 1", "3; 2"], "bad page removal ignored")
    assert_remove(b, -12, ["1; 1", "3; 2"], "bad page removal ignored")
    assert_remove(b, 0, ["1; 1", "3; 2"], "bad page removal ignored")
    assert_remove(b, 1, ["3; 1"], "1st removed")
    assert_remove(b, 1, ["3; 1"], "can't remove sole page")
