"""
Book domain objects.
"""

from lute.models.book import BookTag, Book as DBBook, Text as DBText
from lute.models.repositories import (
    BookRepository,
    BookTagRepository,
    LanguageRepository,
)


def token_group_generator(tokens, group_type, threshold=500):
    """
    A generator that yields groups of ParsedTokens grouped by sentence or paragraph
    with each group containing at least the threshold number of tokens.
    """
    current_group = []
    buff = []

    def trim_paras(tok_array):
        "Remove para tokens from beginning and end."
        while tok_array and tok_array[0].is_end_of_paragraph:
            tok_array.pop(0)
        while tok_array and tok_array[-1].is_end_of_paragraph:
            tok_array.pop()
        return tok_array

    def _matches_group_delimiter(tok):
        if group_type == "sentences":
            return tok.is_end_of_sentence
        if group_type == "paragraphs":
            return tok.is_end_of_paragraph
        raise RuntimeError("Unhandled type " + group_type)

    for token in tokens:
        buff.append(token)
        if _matches_group_delimiter(token):
            current_group.extend(buff)
            # pylint: disable=consider-using-generator
            current_count = sum([1 for t in current_group if t.is_word])
            buff = []

            # Yield if threshold exceeded.
            # Remove the final paragreph marker if it's there, it's not needed.
            if current_count > threshold:
                current_group = trim_paras(current_group)
                yield current_group
                current_group = []

    # Add any remaining tokens
    if buff:
        current_group.extend(buff)
    current_group = trim_paras(current_group)
    if current_group:
        yield current_group


class Book:  # pylint: disable=too-many-instance-attributes
    """
    A book domain object, to create/edit lute.models.book.Books.

    Book language can be specified either by language_id, or
    language_name.  language_name is useful for loading books via
    scripts/api.  language_id takes precedence.
    """

    def __init__(self):
        self.id = None
        self.language_id = None
        self.language_name = None
        self.title = None
        self.text = None
        self.source_uri = None
        self.audio_filename = None
        self.audio_current_pos = None
        self.audio_bookmarks = None
        self.book_tags = []

        self.threshold_page_tokens = 250
        self.split_by = "paragraphs"

        # The source file used for the book text.
        # Overrides the self.text if not None.
        self.text_source_path = None

        self.text_stream = None
        self.text_stream_filename = None

        # The source file used for audio.
        self.audio_source_path = None

        self.audio_stream = None
        self.audio_stream_filename = None

    def __repr__(self):
        return f"<Book (id={self.id}, title='{self.title}')>"

    def add_tag(self, tag):
        self.book_tags.append(tag)


class Repository:
    """
    Maps Book BO to and from lute.model.Book.
    """

    def __init__(self, _session):
        self.session = _session
        self.book_repo = BookRepository(self.session)

    def load(self, book_id):
        "Loads a Book business object for the DBBook."
        dbb = self.book_repo.find(book_id)
        if dbb is None:
            raise ValueError(f"No book with id {book_id} found")
        return self._build_business_book(dbb)

    def find_by_title(self, book_title, language_id):
        "Loads a Book business object for the book with a given title."
        dbb = self.book_repo.find_by_title(book_title, language_id)
        if dbb is None:
            return None
        return self._build_business_book(dbb)

    def get_book_tags(self):
        "Get all available book tags, helper method."
        bts = self.session.query(BookTag).all()
        return sorted([t.text for t in bts])

    def add(self, book):
        """
        Add a book to be saved to the db session.
        Returns DBBook for tests and verification only,
        clients should not change it.
        """
        dbbook = self._build_db_book(book)
        self.session.add(dbbook)
        return dbbook

    def delete(self, book):
        """
        Delete.
        """
        if book.id is None:
            raise ValueError(f"book {book.title} not saved")
        b = self.book_repo.find(book.id)
        self.session.delete(b)

    def commit(self):
        """
        Commit everything.
        """
        self.session.commit()

    def _split_text_at_page_breaks(self, txt):
        "Break fulltext manually at lines consisting of '---' only."
        # Tried doing this with a regex without success.
        segments = []
        current_segment = ""
        for line in txt.split("\n"):
            if line.strip() == "---":
                segments.append(current_segment.strip())
                current_segment = ""
            else:
                current_segment += line + "\n"
        if current_segment:
            segments.append(current_segment.strip())
        return segments

    def _split_pages(self, book, language):
        "Split fulltext into pages, respecting sentences."

        pages = []
        for segment in self._split_text_at_page_breaks(book.text):
            tokens = language.parser.get_parsed_tokens(segment, language)
            for toks in token_group_generator(
                tokens, book.split_by, book.threshold_page_tokens
            ):
                s = "".join([t.token for t in toks])
                s = s.replace("\r", "").replace("¶", "\n")
                pages.append(s.strip())
        pages = [p for p in pages if p.strip() != ""]

        return pages

    def _build_db_book(self, book):
        "Convert a book business object to a DBBook."

        lang_repo = LanguageRepository(self.session)
        lang = None
        if book.language_id:
            lang = lang_repo.find(book.language_id)
        elif book.language_name:
            lang = lang_repo.find_by_name(book.language_name)
        if lang is None:
            msg = f"No language matching id={book.language_id} or name={book.language_name}"
            raise RuntimeError(msg)

        b = None
        if book.id is None:
            pages = self._split_pages(book, lang)
            b = DBBook(book.title, lang)
            for index, page in enumerate(pages):
                _ = DBText(b, page, index + 1)
        else:
            b = self.book_repo.find(book.id)

        b.title = book.title
        b.source_uri = book.source_uri
        b.audio_filename = book.audio_filename
        b.audio_current_pos = book.audio_current_pos
        b.audio_bookmarks = book.audio_bookmarks

        btr = BookTagRepository(self.session)
        booktags = []
        for s in book.book_tags:
            booktags.append(btr.find_or_create_by_text(s))
        b.remove_all_book_tags()
        for tt in booktags:
            b.add_book_tag(tt)

        return b

    def _build_business_book(self, dbbook):
        "Convert db book to Book."
        b = Book()
        b.id = dbbook.id
        b.language_id = dbbook.language.id
        b.language_name = dbbook.language.name
        b.title = dbbook.title
        b.text = None  # Not returning this for now
        b.source_uri = dbbook.source_uri
        b.audio_filename = dbbook.audio_filename
        b.audio_current_pos = dbbook.audio_current_pos
        b.audio_bookmarks = dbbook.audio_bookmarks
        b.book_tags = [t.text for t in dbbook.book_tags]
        return b
