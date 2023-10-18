"""
Book entity.
"""

from lute.db import db
from lute.utils.data_tables import DataTablesSqliteQuery


booktags = db.Table(
    'booktags',
    db.Model.metadata,
    db.Column('BtT2ID', db.Integer, db.ForeignKey('tags2.T2ID')),
    db.Column('BtBkID', db.Integer, db.ForeignKey('books.BkID'))
)


class BookTag(db.Model):
    "Term tags."
    __tablename__ = 'tags2'

    id = db.Column('T2ID', db.Integer, primary_key=True)
    text = db.Column('T2Text', db.String(20))
    comment = db.Column('T2Comment', db.String(200))

    books = db.relationship('Book', secondary=booktags, back_populates='book_tags')

    @staticmethod
    def make_book_tag(text, comment=''):
        "Create a TermTag."
        tt = BookTag()
        tt.text = text
        tt.comment = comment
        return tt


class Book(db.Model): # pylint: disable=too-few-public-methods, too-many-instance-attributes
    """
    Book entity.
    """

    __tablename__ = 'books'

    id = db.Column('BkID', db.SmallInteger, primary_key=True)
    title = db.Column('BkTitle', db.String(length=200))
    lg_id = db.Column('BkLgID', db.Integer, db.ForeignKey('languages.LgID'), nullable=False)
    word_count = db.Column('BkWordCount', db.Integer)
    source_uri = db.Column('BkSourceURI', db.String(length=1000))
    current_tx_id = db.Column('BkCurrentTxID', db.Integer, default=0)
    archived = db.Column('BkArchived', db.Boolean, default=False)

    language = db.relationship('Language')
    texts = db.relationship('Text', back_populates='book', order_by='Text.order')
    book_tags = db.relationship('BookTag', secondary='booktags', back_populates='books')

    def __init__(self, title=None, language=None, source_uri=None):
        self.title = title
        self.language = language
        self.source_uri = source_uri
        self.texts = []
        self.book_tags = []

    def __repr__(self):
        return f"<Book {self.id} {self.title}>"


    # TODO book listing: update to new code in lutev2
    @staticmethod
    def get_data_tables_list(parameters, is_archived):
        "Book json data for datatables."

        archived = 'true' if is_archived else 'false'

        base_sql = f"""
        SELECT
            b.BkID As BkID,
            LgName,
            BkTitle,
            case when currtext.TxID is null then 1 else currtext.TxOrder end as PageNum,
            pagecnt.c as PageCount,
            BkArchived,
            tags.taglist AS TagList,
            case when ifnull(b.BkWordCount, 0) = 0 then 'n/a' else b.BkWordCount end as WordCount,
            c.distinctterms as DistinctCount,
            c.distinctunknowns as UnknownCount,
            c.unknownpercent as UnknownPercent

        FROM books b
        INNER JOIN languages ON LgID = b.BkLgID
        LEFT OUTER JOIN texts currtext ON currtext.TxID = BkCurrentTxID
        INNER JOIN (
            SELECT TxBkID, COUNT(TxID) AS c FROM texts
            GROUP BY TxBkID
        ) pagecnt on pagecnt.TxBkID = b.BkID
        LEFT OUTER JOIN bookstats c on c.BkID = b.BkID
        LEFT OUTER JOIN (
            SELECT BtBkID as BkID, GROUP_CONCAT(T2Text, ', ') AS taglist
            FROM
            (
                SELECT BtBkID, T2Text
                FROM booktags bt
                INNER JOIN tags2 t2 ON t2.T2ID = bt.BtT2ID
                ORDER BY T2Text
            ) tagssrc
            GROUP BY BtBkID
        ) AS tags ON tags.BkID = b.BkID

        WHERE b.BkArchived = {archived}
        """

        session = db.session
        connection = session.connection()

        return DataTablesSqliteQuery.get_data(base_sql, parameters, connection)


class Text(db.Model):
    """
    Each page in a Book.

    This class should really be named "Page" ...
    todo for the future.
    """
    __tablename__ = 'texts'

    id = db.Column('TxID', db.Integer, primary_key=True)
    _text = db.Column('TxText', db.String, nullable=False)
    order = db.Column('TxOrder', db.Integer)
    _read_date = db.Column('TxReadDate', db.DateTime, nullable=True)
    bk_id = db.Column('TxBkID', db.Integer, db.ForeignKey('books.BkID'), nullable=False)

    book = db.relationship('Book', back_populates='texts')
    sentences = db.relationship('Sentence', back_populates='text', order_by='Sentence.order')

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


class Sentence(db.Model):
    """
    Parsed sentences for a given Text.

    The Sentence contains the parsed tokens, joined by the zero-width string.
    """

    __tablename__ = 'sentences'

    id = db.Column('SeID', db.Integer, primary_key=True)
    tx_id = db.Column('SeTxID', db.Integer, db.ForeignKey('texts.TxID'), nullable=False)
    order = db.Column('SeOrder', db.Integer, default=1)
    text_content = db.Column('SeText', db.Text, default='')

    text = db.relationship('Text', back_populates='sentences')

    def __init__(self, text_content='', text=None, order=1):
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
        s = s.strip(' ')

        # The zws is added at the start and end of each
        # sentence, to standardize the string search when
        # looking for terms.
        s = zws + s + zws

        sentence = Sentence()
        sentence.order = senumber
        sentence.text_content = s
        return sentence
