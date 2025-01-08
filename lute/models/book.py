"""
Book entity.
"""

import sqlite3
from contextlib import closing
from lute.db import db

booktags = db.Table(
    "booktags",
    db.Model.metadata,
    db.Column("BtT2ID", db.Integer, db.ForeignKey("tags2.T2ID")),
    db.Column("BtBkID", db.Integer, db.ForeignKey("books.BkID")),
)


class BookTag(db.Model):
    "Term tags."
    __tablename__ = "tags2"

    id = db.Column("T2ID", db.Integer, primary_key=True)
    text = db.Column("T2Text", db.String(20))
    comment = db.Column("T2Comment", db.String(200))

    @staticmethod
    def make_book_tag(text, comment=""):
        "Create a BookTag."
        tt = BookTag()
        tt.text = text
        tt.comment = comment
        return tt


class Book(
    db.Model
):  # pylint: disable=too-few-public-methods, too-many-instance-attributes
    """
    Book entity.
    """

    __tablename__ = "books"

    id = db.Column("BkID", db.SmallInteger, primary_key=True)
    title = db.Column("BkTitle", db.String(length=200))
    language_id = db.Column(
        "BkLgID", db.Integer, db.ForeignKey("languages.LgID"), nullable=False
    )
    source_uri = db.Column("BkSourceURI", db.String(length=1000))
    current_tx_id = db.Column("BkCurrentTxID", db.Integer, default=0)
    archived = db.Column("BkArchived", db.Boolean, default=False)

    audio_filename = db.Column("BkAudioFilename", db.String)
    audio_current_pos = db.Column("BkAudioCurrentPos", db.Float)
    audio_bookmarks = db.Column("BkAudioBookmarks", db.String)

    language = db.relationship("Language")
    texts = db.relationship(
        "Text",
        back_populates="book",
        order_by="Text.order",
        cascade="all, delete-orphan",
    )
    book_tags = db.relationship("BookTag", secondary="booktags")

    def __init__(self, title=None, language=None, source_uri=None):
        self.title = title
        self.language = language
        self.source_uri = source_uri
        self.texts = []
        self.book_tags = []

    def __repr__(self):
        return f"<Book {self.id} {self.title}>"

    def remove_all_book_tags(self):
        self.book_tags = []

    def add_book_tag(self, book_tag):
        if book_tag not in self.book_tags:
            self.book_tags.append(book_tag)

    def remove_book_tag(self, book_tag):
        self.book_tags.remove(book_tag)

    @property
    def page_count(self):
        return len(self.texts)

    def page_in_range(self, n):
        "Return page number that is in the book's page count."
        ret = max(n, 1)
        ret = min(ret, self.page_count)
        return ret

    def text_at_page(self, n):
        "Return the text object at page n."
        pagenum = self.page_in_range(n)
        return self.texts[pagenum - 1]

    def _add_page(self, new_pagenum):
        "Add new page, increment other page orders."
        pages_after = [t for t in self.texts if t.order >= new_pagenum]
        for t in pages_after:
            t.order = t.order + 1
        t = Text(None, "", new_pagenum)
        # TODO fix_refs: None first arg is garbage code.  Passing self
        # as the text's book causes a "SAWarning: Object of type
        # <Text> not in session, add operation along 'Book.texts' will
        # not proceed" warning ... so adding the text to the book
        # manually is needed.  The book's language is required to
        # correctly parse the Text's text though ...
        self.texts.append(t)
        return t

    def add_page_before(self, pagenum):
        "Add page before page n, renumber all subsequent pages, return new page."
        return self._add_page(self.page_in_range(pagenum))

    def add_page_after(self, pagenum):
        "Add page after page n, renumber all subsequent pages, return new page."
        return self._add_page(self.page_in_range(pagenum) + 1)

    def remove_page(self, pagenum):
        "Remove page, renumber all subsequent pages."
        # Don't delete page of single-page books.
        if len(self.texts) == 1:
            return
        texts = [t for t in self.texts if t.order == pagenum]
        if len(texts) == 0:
            return
        texts[0].book = None
        pages_after = [t for t in self.texts if t.order > pagenum]
        for t in pages_after:
            t.order = t.order - 1

    @property
    def is_supported(self):
        "True if the book's language's parser is supported."
        return self.language.is_supported


# TODO zzfuture fix: rename class and table to Page/pages
class Text(db.Model):
    """
    Each page in a Book.
    """

    __tablename__ = "texts"

    id = db.Column("TxID", db.Integer, primary_key=True)
    _text = db.Column("TxText", db.String, nullable=False)
    order = db.Column("TxOrder", db.Integer)
    start_date = db.Column("TxStartDate", db.DateTime, nullable=True)
    _read_date = db.Column("TxReadDate", db.DateTime, nullable=True)
    bk_id = db.Column("TxBkID", db.Integer, db.ForeignKey("books.BkID"), nullable=False)
    word_count = db.Column("TxWordCount", db.Integer, nullable=True)

    book = db.relationship("Book", back_populates="texts")
    bookmarks = db.relationship(
        "TextBookmark",
        back_populates="text",
        cascade="all, delete-orphan",
    )
    sentences = db.relationship(
        "Sentence",
        back_populates="text",
        order_by="Sentence.order",
        cascade="all, delete-orphan",
    )

    def __init__(self, book, text, order=1):
        self.book = book
        self.text = text
        self.order = order
        self.sentences = []

    @property
    def title(self):
        """
        Text title is the book title + page fraction.
        """
        b = self.book
        s = f"({self.order}/{self.book.page_count})"
        t = f"{b.title} {s}"
        return t

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, s):
        self._text = s
        if s.strip() == "":
            return
        toks = self._get_parsed_tokens()
        wordtoks = [t for t in toks if t.is_word]
        self.word_count = len(wordtoks)
        if self._read_date is not None:
            self._load_sentences_from_tokens(toks)

    @property
    def read_date(self):
        return self._read_date

    @read_date.setter
    def read_date(self, s):
        self._read_date = s
        # Ensure loaded.
        self.load_sentences()

    def _get_parsed_tokens(self):
        "Return the tokens."
        lang = self.book.language
        return lang.parser.get_parsed_tokens(self.text, lang)

    def _load_sentences_from_tokens(self, parsedtokens):
        "Save sentences using the tokens."
        parser = self.book.language.parser
        self._remove_sentences()
        curr_sentence_tokens = []
        sentence_num = 1

        def _add_current():
            "Create and add sentence from current state."
            if curr_sentence_tokens:
                se = Sentence.from_tokens(curr_sentence_tokens, parser, sentence_num)
                self._add_sentence(se)
            # Reset for the next sentence.
            curr_sentence_tokens.clear()

        for pt in parsedtokens:
            curr_sentence_tokens.append(pt)
            if pt.is_end_of_sentence:
                _add_current()
                sentence_num += 1

        # Add any stragglers.
        _add_current()

    def load_sentences(self):
        """
        Parse the current text and create Sentence objects.
        """
        toks = self._get_parsed_tokens()
        self._load_sentences_from_tokens(toks)

    def _add_sentence(self, sentence):
        "Add a sentence to the Text."
        if sentence not in self.sentences:
            self.sentences.append(sentence)
            sentence.text = self

    def _remove_sentences(self):
        "Remove all sentence from the Text."
        for sentence in self.sentences:
            sentence.text = None
        self.sentences = []


class WordsRead(db.Model):
    """
    Tracks reading events for Text entities.
    """

    __tablename__ = "wordsread"
    id = db.Column("WrID", db.Integer, primary_key=True)
    language_id = db.Column(
        "WrLgID", db.Integer, db.ForeignKey("languages.LgID"), nullable=False
    )
    tx_id = db.Column(
        "WrTxID",
        db.Integer,
        db.ForeignKey("texts.TxID", ondelete="SET NULL"),
        nullable=True,
    )
    read_date = db.Column("WrReadDate", db.DateTime, nullable=False)
    word_count = db.Column("WrWordCount", db.Integer, nullable=False)

    def __init__(self, text, read_date, word_count):
        self.tx_id = text.id
        self.language_id = text.book.language.id
        self.read_date = read_date
        self.word_count = word_count


class Sentence(db.Model):
    """
    Parsed sentences for a given Text.

    The Sentence contains the parsed tokens, joined by the zero-width string.
    """

    __tablename__ = "sentences"

    id = db.Column("SeID", db.Integer, primary_key=True)
    tx_id = db.Column("SeTxID", db.Integer, db.ForeignKey("texts.TxID"), nullable=False)
    order = db.Column("SeOrder", db.Integer, default=1)
    text_content = db.Column("SeText", db.Text, default="")
    textlc_content = db.Column("SeTextLC", db.Text)

    text = db.relationship("Text", back_populates="sentences")

    def set_lowercase_text(self, parser):
        """
        Load textlc_content from text_content.

        If a call to sqlite's LOWER() function for the text_content
        returns the same lowercase text as a call to the parser,
        store '*' as the lowercase text.  This seeming hack can save a
        pile of space: for my ~30meg db of ~135K sentences, only 750
        sentences were different when lowercased by the LOWER() vs by
        the parser.

        This method is public for use in the data_cleanup module.
        """

        def _get_sql_lower(input_string):
            "Returns result of sqlite LOWER call of input_string."
            if input_string is None:
                return None
            with sqlite3.connect(":memory:") as conn, closing(conn.cursor()) as cur:
                cur.execute("SELECT LOWER(?)", (input_string,))
                result = cur.fetchone()
                return result[0]

        lcased = parser.get_lowercase(self.text_content)
        if lcased == _get_sql_lower(self.text_content):
            lcased = "*"
        self.textlc_content = lcased

    @staticmethod
    def from_tokens(tokens, parser, senumber):
        """
        Create a new Sentence from ParsedTokens.
        """

        def _sentence_string(string_array):
            "Create properly-zws-joined sentence string."
            zws = chr(0x200B)  # Zero-width space.
            s = zws.join(string_array).strip(" ")
            # The zws is added at the start and end of each
            # sentence, to standardize the string search when
            # looking for terms.
            return zws + s + zws

        sentence = Sentence()
        sentence.order = senumber
        sentence.text_content = _sentence_string([t.token for t in tokens])
        sentence.set_lowercase_text(parser)
        return sentence


class TextBookmark(db.Model):
    """
    Bookmarks for a given Book page

    The TextBookmark includes a title
    """

    __tablename__ = "textbookmarks"

    id = db.Column("TbID", db.Integer, primary_key=True)
    tx_id = db.Column(
        "TbTxID",
        db.Integer,
        db.ForeignKey("texts.TxID", ondelete="CASCADE"),
        nullable=False,
    )
    title = db.Column("TbTitle", db.Text, nullable=False)

    text = db.relationship("Text", back_populates="bookmarks")


class BookStats(db.Model):
    "The stats table."
    __tablename__ = "bookstats"

    BkID = db.Column(db.Integer, primary_key=True)
    distinctterms = db.Column(db.Integer)
    distinctunknowns = db.Column(db.Integer)
    unknownpercent = db.Column(db.Integer)
    status_distribution = db.Column(db.String, nullable=True)
