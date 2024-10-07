"""
Smoke test for bulk import of books.
"""

from lute.cli.import_books import import_books_from_csv

from lute.models.book import Book
from lute.db import db


def test_smoke_test(app_context, tmp_path, english):
    """Test importing books from CSV file"""
    csv_contents = """title,url,tags,an extra column,text
A Book,http://www.example.com/book,"foo,bar,baz",extra information,"Lorem ipsum, dolor sit amet."
Another Book,,,,The quick brown fox jumps over the lazy dog.
"""
    csv_file = tmp_path / 'books.csv'
    with open(csv_file, 'w') as f:
        f.write(csv_contents)
    common_tags = ["bar", "qux"]

    # Check that no changes are made if not committing.
    import_books_from_csv("English", csv_file, common_tags, False)
    assert(Book.find_by_title("A Book") is None)
    assert(Book.find_by_title("Another Book") is None)

    # Check that new books are added.
    import_books_from_csv("English", csv_file, common_tags, True)

    book = Book.find_by_title("A Book")
    assert(book is not None)
    assert(book.title == "A Book")
    assert(book.language_id == english.id)
    assert(book.source_uri == "http://www.example.com/book")
    assert(len(book.texts) == 1)
    assert(book.texts[0].text == "Lorem ipsum, dolor sit amet.")
    assert(sorted([tag.text for tag in book.book_tags]) == ["bar", "baz", "foo", "qux"])

    book = Book.find_by_title("Another Book")
    assert(book is not None)
    assert(book.title == "Another Book")
    assert(book.language_id == english.id)
    assert(book.source_uri is None)
    assert(len(book.texts) == 1)
    assert(book.texts[0].text == "The quick brown fox jumps over the lazy dog.")
    assert(sorted([tag.text for tag in book.book_tags]) == ["bar", "qux"])

    # Check that duplicate books are not added.
    import_books_from_csv("English", csv_file, common_tags, True)

    assert(db.session.query(Book).filter(Book.title == "A Book").count() == 1)
    assert(db.session.query(Book).filter(Book.title == "Another Book").count() == 1)
