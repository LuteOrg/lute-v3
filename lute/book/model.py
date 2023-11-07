"""
Book domain objects.
"""

from lute.models.book import Book as DBBook, BookTag
from lute.models.language import Language


class Book:
    """
    A book domain object, to create/edit lute.models.book.Books.
    """

    def __init__(self):
        self.id = None
        self.language_id = None
        self.title = None
        self.text = None
        self.source_uri = None
        self.book_tags = []

    def __repr__(self):
        return f"<Book (id={self.id}, title='{self.title}')>"

    def add_tag(self, tag):
        self.book_tags.append(tag)


class Repository:
    """
    Maps Book BO to and from lute.model.Book.
    """

    def __init__(self, _db):
        self.db = _db

    def load(self, book_id):
        "Loads a Book business object for the DBBook."
        dbb = DBBook.find(book_id)
        if dbb is None:
            raise ValueError(f"No book with id {book_id} found")
        return self._build_business_book(dbb)

    def get_book_tags(self):
        "Get all available book tags, helper method."
        bts = self.db.session.query(BookTag).all()
        return [t.text for t in bts]

    def add(self, book):
        """
        Add a book to be saved to the db session.
        Returns DBBook for tests and verification only,
        clients should not change it.
        """
        dbbook = self._build_db_book(book)
        self.db.session.add(dbbook)
        return dbbook

    def delete(self, book):
        """
        Delete.
        """
        if book.id is None:
            raise ValueError(f"book {book.title} not saved")
        b = DBBook.find(book.id)
        self.db.session.delete(b)

    def commit(self):
        """
        Commit everything.
        """
        self.db.session.commit()

    def _build_db_book(self, book):
        "Convert a book business object to a DBBook."

        lang = Language.find(book.language_id)

        b = None
        if book.id is None:
            b = DBBook.create_book(book.title, lang, book.text)
        else:
            b = DBBook.find(book.id)
        b.title = book.title
        b.source_uri = book.source_uri

        booktags = []
        for s in book.book_tags:
            booktags.append(BookTag.find_or_create_by_text(s))
        b.remove_all_book_tags()
        for tt in booktags:
            b.add_book_tag(tt)

        return b

    def _build_business_book(self, dbbook):
        "Convert db book to Book."
        b = Book()
        b.id = dbbook.id
        b.language_id = dbbook.language.id
        b.title = dbbook.title
        b.text = None  # Not returning this for now
        b.source_uri = dbbook.source_uri
        b.book_tags = [t.text for t in dbbook.book_tags]
        return b
