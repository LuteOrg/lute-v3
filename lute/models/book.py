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

    @staticmethod
    def create_book(title, language, fulltext, max_word_tokens_per_text=250):
        """
        Create a book with given fulltext content,
        splitting the content into separate Text objects with max
        token count.
        """

        def split_text_at_page_breaks(txt):
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

        pages = []
        for segment in split_text_at_page_breaks(fulltext):
            tokens = language.parser.get_parsed_tokens(segment, language)
            it = SentenceGroupIterator(tokens, max_word_tokens_per_text)
            while toks := it.next():
                s = (
                    "".join([t.token for t in toks])
                    .replace("\r", "")
                    .replace("¶", "\n")
                    .strip()
                )
                pages.append(s)
        pages = [p for p in pages if p.strip() != ""]

        b = Book(title, language)
        for index, page in enumerate(pages):
            t = Text(b, page, index + 1)

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
        self._remove_sentences()
        curr_sentence_tokens = []
        sentence_number = 1
        for pt in parsedtokens:
            curr_sentence_tokens.append(pt)
            if pt.is_end_of_sentence:
                se = Sentence.from_tokens(curr_sentence_tokens, sentence_number)
                self._add_sentence(se)
                # Reset for the next sentence.
                curr_sentence_tokens = []
                sentence_number += 1

        # Add any stragglers.
        if len(curr_sentence_tokens) > 0:
            se = Sentence.from_tokens(curr_sentence_tokens, sentence_number)
            self._add_sentence(se)

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
