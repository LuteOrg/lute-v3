"""
TextBookmark mapping checks.
"""
from datetime import datetime
import pytest
from lute.models.book import Book, Text, TextBookmark
from lute.db import db
from tests.dbasserts import assert_record_count_equals, assert_sql_result


@pytest.fixture(name="sample_book")
def fixture_sample_book(english):
    "Sample Book"
    b = Book.create_book("Book Title", english, "some text")
    b.texts[0].read_date = datetime.now()
    return b


@pytest.fixture(name="sample_text")
def fixture_sample_text(sample_book: Book):
    "Sample Text"
    t = Text(sample_book, "test text", 1)
    return t


@pytest.fixture(name="sample_textbookmark")
def fixture_sample_bookmark(sample_text: Text):
    "Sample TextBookmark"
    tb = TextBookmark(text=sample_text, title="Test Title")
    return tb


def test_save_textbookmark(
    empty_db, sample_textbookmark: TextBookmark, sample_text: Text
):
    """Check TextBookmark mappings"""
    db.session.add(sample_text)
    db.session.add(sample_textbookmark)
    db.session.commit()
    sql = "SELECT TbTxId, TbTitle FROM textbookmarks"
    assert_sql_result(
        sql, [f"{sample_text.id}; {sample_textbookmark.title}"], "textbookmark"
    )


def test_edit_textbookmark(
    empty_db, sample_textbookmark: TextBookmark, sample_text: Text
):
    """Edit TextBookmark"""
    db.session.add(sample_text)
    db.session.add(sample_textbookmark)
    db.session.commit()

    db.session.query(TextBookmark).filter(
        TextBookmark.text.has(id=sample_text.id)
    ).update({"title": "New Title"})
    db.session.commit()

    sql = "SELECT TbTxId, TbTitle FROM textbookmarks"
    assert_sql_result(sql, [f"{sample_text.id}; New Title"], "textbookmark")


def test_delete_textbookmark(
    empty_db, sample_textbookmark: TextBookmark, sample_text: Text
):
    """Delete TextBookmark"""
    db.session.add(sample_text)
    db.session.add(sample_textbookmark)
    db.session.commit()

    db.session.query(TextBookmark).filter(
        TextBookmark.text.has(id=sample_text.id)
    ).delete()
    db.session.commit()

    assert_record_count_equals("textbookmarks", 0, "0 bookmarks")
