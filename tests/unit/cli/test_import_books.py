"""
Smoke test for bulk import of books.
"""

from sqlalchemy import and_
from lute.cli.import_books import import_books_from_csv
from lute.models.book import Book
from lute.models.repositories import BookRepository
from lute.db import db


def test_smoke_test(app_context, tmp_path, english, german):
    """Test importing books from CSV file"""
    csv_contents = """title,language,url,tags,audio,bookmarks,an extra column,text
A Book,English,http://www.example.com/book,"foo,bar,baz",book.mp3,1.00;3.14;42.00,extra information,"Lorem ipsum, dolor sit amet."
Another Book,,,,,,,The quick brown fox jumps over the lazy dog.
A Book,German,,,,,,Zwölf Boxkämpfer jagen Viktor quer über den großen Sylter Deich.
"""
    csv_file = tmp_path / "books.csv"
    with open(csv_file, "w", encoding="utf-8") as f:
        f.write(csv_contents)
    mp3_file = tmp_path / "book.mp3"
    with open(mp3_file, "w", encoding="utf-8") as f:
        pass

    common_tags = ["bar", "qux"]

    repo = BookRepository(db.session)

    # Check that no changes are made if not committing.
    import_books_from_csv(csv_file, "English", common_tags, False)
    assert repo.find_by_title("A Book", english.id) is None
    assert repo.find_by_title("Another Book", english.id) is None
    assert repo.find_by_title("A Book", german.id) is None

    # Check that new books are added.
    import_books_from_csv(csv_file, "English", common_tags, True)

    book = repo.find_by_title("A Book", english.id)
    assert book is not None
    assert book.title == "A Book"
    assert book.language_id == english.id
    assert book.source_uri == "http://www.example.com/book"
    assert book.audio_filename == str(mp3_file)
    assert book.audio_bookmarks == "1.00;3.14;42.00"
    assert len(book.texts) == 1
    assert book.texts[0].text == "Lorem ipsum, dolor sit amet."
    assert sorted([tag.text for tag in book.book_tags]) == ["bar", "baz", "foo", "qux"]

    book = repo.find_by_title("Another Book", english.id)
    assert book is not None
    assert book.title == "Another Book"
    assert book.language_id == english.id
    assert book.source_uri is None
    assert book.audio_filename is None
    assert book.audio_bookmarks is None
    assert len(book.texts) == 1
    assert book.texts[0].text == "The quick brown fox jumps over the lazy dog."
    assert sorted([tag.text for tag in book.book_tags]) == ["bar", "qux"]

    book = repo.find_by_title("A Book", german.id)
    assert book is not None
    assert book.title == "A Book"
    assert book.language_id == german.id
    assert book.source_uri is None
    assert book.audio_filename is None
    assert book.audio_bookmarks is None
    assert len(book.texts) == 1
    assert (
        book.texts[0].text
        == "Zwölf Boxkämpfer jagen Viktor quer über den großen Sylter Deich."
    )
    assert sorted([tag.text for tag in book.book_tags]) == ["bar", "qux"]

    # Check that duplicate books are not added.
    import_books_from_csv(csv_file, "English", common_tags, True)

    assert (
        db.session.query(Book)
        .filter(and_(Book.title == "A Book", Book.language_id == english.id))
        .count()
        == 1
    )
    assert (
        db.session.query(Book)
        .filter(and_(Book.title == "Another Book", Book.language_id == english.id))
        .count()
        == 1
    )
    assert (
        db.session.query(Book)
        .filter(and_(Book.title == "A Book", Book.language_id == german.id))
        .count()
        == 1
    )
