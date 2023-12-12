"""
Book entity.
"""

from lute.db import db
from lute.parse.base import SentenceGroupIterator

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

    @staticmethod
    def find_by_text(text):
        "Find a tag by text, or None if not found."
        return db.session.query(BookTag).filter(BookTag.text == text).first()

    @staticmethod
    def find_or_create_by_text(text):
        "Return tag or create one."
        ret = BookTag.find_by_text(text)
        if ret is not None:
            return ret
        return BookTag.make_book_tag(text)


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
    word_count = db.Column("BkWordCount", db.Integer)
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

    @property
    def is_supported(self):
        "True if the book's language's parser is supported."
        return self.language.is_supported

    @staticmethod
    def create_book(title, language, fulltext, max_word_tokens_per_text=250):
        """
        Create a book with given fulltext content,
        splitting the content into separate Text objects with max
        token count.
        """
        tokens = language.parser.get_parsed_tokens(fulltext, language)

        def token_string(toks):
            a = [t.token for t in toks]
            ret = "".join(a)
            ret = ret.replace("\r", "")
            ret = ret.replace("¶", "\n")
            return ret.strip()

        b = Book(title, language)
        b.word_count = len([t for t in tokens if t.is_word])

        page_number = 0
        it = SentenceGroupIterator(tokens, max_word_tokens_per_text)
        while toks := it.next():
            page_number += 1
            # Note the text is automatically added to b.texts!
            t = Text(b, token_string(toks), page_number)

        return b

    @staticmethod
    def find(book_id):
        "Get by ID."
        return db.session.query(Book).filter(Book.id == book_id).first()


# TODO zzfuture fix: rename class and table to Page/pages
class Text(db.Model):
    """
    Each page in a Book.
    """

    __tablename__ = "texts"

    id = db.Column("TxID", db.Integer, primary_key=True)
    _text = db.Column("TxText", db.String, nullable=False)
    order = db.Column("TxOrder", db.Integer)
    _read_date = db.Column("TxReadDate", db.DateTime, nullable=True)
    bk_id = db.Column("TxBkID", db.Integer, db.ForeignKey("books.BkID"), nullable=False)
    word_count = db.Column("TxWordCount", db.Integer, nullable=True)

    book = db.relationship("Book", back_populates="texts")
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
        self._load_sentences()

    @property
    def read_date(self):
        return self._read_date

    @read_date.setter
    def read_date(self, s):
        self._read_date = s
        self._load_sentences()

    def _load_sentences(self):
        """
        Parse the current text and create Sentence objects.
        Sentences are only needed once the text has been read.
        """
        self.remove_sentences()

        if self.read_date is None:
            return

        lang = self.book.language
        parser = lang.parser
        parsedtokens = parser.get_parsed_tokens(self.text, lang)

        curr_sentence_tokens = []
        sentence_number = 1

        for pt in parsedtokens:
            curr_sentence_tokens.append(pt)
            if pt.is_end_of_sentence:
                se = Sentence.from_tokens(curr_sentence_tokens, sentence_number)
                self.add_sentence(se)

                # Reset for the next sentence.
                curr_sentence_tokens = []
                sentence_number += 1

        # Add any stragglers.
        if len(curr_sentence_tokens) > 0:
            se = Sentence.from_tokens(curr_sentence_tokens, sentence_number)
            self.add_sentence(se)

    def add_sentence(self, sentence):
        "Add a sentence to the Text."
        if sentence not in self.sentences:
            self.sentences.append(sentence)
            sentence.text = self

    def remove_sentences(self):
        "Remove all sentence from the Text."
        for sentence in self.sentences:
            sentence.text = None
        self.sentences = []

    @staticmethod
    def find(text_id):
        "Get by ID."
        return db.session.query(Text).filter(Text.id == text_id).first()


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

    text = db.relationship("Text", back_populates="sentences")

    def __init__(self, text_content="", text=None, order=1):
        self.text_content = text_content
        self.text = text
        self.order = order

    @staticmethod
    def from_tokens(tokens, senumber):
        """
        Create a new Sentence from ParsedTokens.
        """

        ptstrings = [t.token for t in tokens]

        zws = chr(0x200B)  # Zero-width space.
        s = zws.join(ptstrings)
        s = s.strip(" ")

        # The zws is added at the start and end of each
        # sentence, to standardize the string search when
        # looking for terms.
        s = zws + s + zws

        sentence = Sentence()
        sentence.order = senumber
        sentence.text_content = s
        return sentence
