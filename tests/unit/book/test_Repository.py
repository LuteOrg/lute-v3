"""
Book Repository tests.

Tests lute.term.model.Book *domain* objects being saved
and retrieved from DB.
"""

import pytest

from lute.db import db
from lute.book.model import Book, Repository
from tests.dbasserts import assert_sql_result


@pytest.fixture(name="repo")
def fixture_repo():
    return Repository(db)


@pytest.fixture(name="new_book")
def fixture_book(english):
    """
    Term business object with some defaults,
    no tags or parents.
    """
    b = Book()
    b.language_id = english.id
    b.title = "HELLO"
    b.text = "greeting"
    b.source_uri = "somesource"
    b.book_tags = ["tag1", "tag2"]
    return b


def test_save_new(app_context, new_book, repo):
    """
    Saving a simple Book object loads the database.
    """
    sql = "select BkTitle from books where BkTitle = 'HELLO'"
    assert_sql_result(sql, [], "empty table")

    b = repo.add(new_book)
    repo.commit()
    assert_sql_result(sql, ["HELLO"], "Saved")
    assert b.texts[0].text == "greeting"

    book = repo.load(b.id)
    assert book.title == new_book.title, "found book"
    assert book.book_tags == ["tag1", "tag2"], "tags filled"


def test_can_save_new_book_by_language_name(app_context, new_book, repo):
    """
    Can save a book with language name, useful for api access.
    """
    sql = "select BkTitle from books where BkTitle = 'HELLO'"
    assert_sql_result(sql, [], "empty table")

    new_book.language_id = None
    new_book.language_name = "English"
    b = repo.add(new_book)
    repo.commit()
    assert_sql_result(sql, ["HELLO"], "Saved")
    assert b.texts[0].text == "greeting"

    book = repo.load(b.id)
    assert book.title == new_book.title, "found book"
    assert book.book_tags == ["tag1", "tag2"], "tags filled"


def test_save_new_respects_book_words_per_page_count(app_context, new_book, repo):
    """
    Saving a simple Book object loads the database.
    """
    sql = "select BkTitle from books where BkTitle = 'HELLO'"
    assert_sql_result(sql, [], "empty table")

    new_book.max_page_tokens = 10
    new_book.text = (
        "One two three four. One two three four five six seven eight nine ten eleven."
    )
    b = repo.add(new_book)
    repo.commit()
    assert_sql_result(sql, ["HELLO"], "Saved")
    assert b.texts[0].text == "One two three four.", "page 1"
    assert (
        b.texts[1].text == "One two three four five six seven eight nine ten eleven."
    ), "page 2"

    book = repo.load(b.id)
    assert book.title == new_book.title, "found book"
    assert book.book_tags == ["tag1", "tag2"], "tags filled"


def test_get_tags(app_context, new_book, repo):
    "Helper method test."
    assert repo.get_book_tags() == [], "no tags yet"
    repo.add(new_book)
    repo.commit()
    assert repo.get_book_tags() == ["tag1", "tag2"], "no tags yet"


def test_save_update_existing(app_context, new_book, repo):
    "Update an existing book, tags are replaced."
    b = repo.add(new_book)
    repo.commit()
    assert_sql_result(
        "select BkTitle from books where BkTitle = 'HELLO'", ["HELLO"], "Saved"
    )

    book = repo.load(b.id)
    book.title = "CHANGED"
    book.book_tags = ["new1", "new2"]
    repo.add(book)
    repo.commit()

    assert_sql_result(
        "select BkTitle from books where BkTitle = 'CHANGED'", ["CHANGED"], "ok"
    )
    assert_sql_result(
        "select T2Text from tags2 order by T2Text", ["new1", "new2", "tag1", "tag2"]
    )


## Deletes.


def test_delete(app_context, new_book, repo):
    "Delete removes book, book must have an id."
    with pytest.raises(ValueError):
        repo.delete(new_book)

    b = repo.add(new_book)
    repo.commit()
    sql = "select BkTitle from books where BkTitle = 'HELLO'"
    assert_sql_result(sql, ["HELLO"], "Saved")

    foundbook = repo.load(b.id)
    repo.delete(foundbook)
    repo.commit()
    assert_sql_result(sql, [], "Deleted")
