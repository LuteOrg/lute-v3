"""
Term entity.
"""

from sqlalchemy import text as sqltext, and_
from lute.db import db

wordparents = db.Table(
    "wordparents",
    db.Model.metadata,
    db.Column("WpWoID", db.Integer, db.ForeignKey("words.WoID")),
    db.Column("WpParentWoID", db.Integer, db.ForeignKey("words.WoID")),
)


class TermImage(db.Model):
    "Term images."
    __tablename__ = "wordimages"

    id = db.Column("WiID", db.Integer, primary_key=True)
    term_id = db.Column(
        "WiWoID", db.Integer, db.ForeignKey("words.WoID"), nullable=False
    )
    term = db.relationship("Term", back_populates="images")
    source = db.Column("WiSource", db.String(500))


class TermFlashMessage(db.Model):
    "Term flash messages."
    __tablename__ = "wordflashmessages"

    id = db.Column("WfID", db.Integer, primary_key=True)
    message = db.Column("WfMessage", db.String(200))
    term_id = db.Column(
        db.Integer, db.ForeignKey("words.WoID"), name="WfWoID", nullable=False
    )
    term = db.relationship("Term", back_populates="term_flash_message", uselist=False)


wordtags = db.Table(
    "wordtags",
    db.Model.metadata,
    db.Column("WtTgID", db.Integer, db.ForeignKey("tags.TgID")),
    db.Column("WtWoID", db.Integer, db.ForeignKey("words.WoID")),
)


class TermTag(db.Model):
    "Term tags."
    __tablename__ = "tags"

    id = db.Column("TgID", db.Integer, primary_key=True)
    text = db.Column("TgText", db.String(20))
    _comment = db.Column("TgComment", db.String(200))

    def __init__(self, text, comment=None):
        self.text = text
        self.comment = comment

    @property
    def comment(self):
        "Comment getter."
        return self._comment

    # TODO zzfuture fix: TgComment should be nullable
    # The current schema has the TgComment NOT NULL default '',
    # which was a legacy copy over from LWT. Really, this should
    # be a nullable column, and all blanks should be NULL.
    # Minor change, a nice-to-have.
    @comment.setter
    def comment(self, c):
        "Set cleaned comment."
        self._comment = c if c is not None else ""

    @staticmethod
    def find(termtag_id):
        "Get by ID."
        return db.session.query(TermTag).filter(TermTag.id == termtag_id).first()

    @staticmethod
    def find_by_text(text):
        "Find a tag by text, or None if not found."
        return db.session.query(TermTag).filter(TermTag.text == text).first()

    @staticmethod
    def find_or_create_by_text(text):
        "Return tag or create one."
        ret = TermTag.find_by_text(text)
        if ret is not None:
            return ret
        return TermTag(text)


class TermTextChangedException(Exception):
    """
    Terms cannot change their text once saved,
    except for the text case.
    """


class Term(
    db.Model
):  # pylint: disable=too-few-public-methods, too-many-instance-attributes
    """
    Term entity.
    """

    __tablename__ = "words"

    id = db.Column("WoID", db.SmallInteger, primary_key=True)
    language_id = db.Column("WoLgID", db.Integer, db.ForeignKey("languages.LgID"))

    # Text should only be set through setters.
    _text = db.Column("WoText", db.String(250))

    # text_lc shouldn't be touched (it's changed when term.text is
    # set), but it's public here to allow for its access during
    # queries (eg in lute.read.service.  This can probably be
    # improved, not sure how at the moment.
    text_lc = db.Column("WoTextLC", db.String(250))

    status = db.Column("WoStatus", db.Integer)
    translation = db.Column("WoTranslation", db.String(500))
    romanization = db.Column("WoRomanization", db.String(100))
    token_count = db.Column("WoTokenCount", db.Integer)
    sync_status = db.Column("WoSyncStatus", db.Boolean)

    language = db.relationship("Language")
    term_tags = db.relationship("TermTag", secondary="wordtags")
    parents = db.relationship(
        "Term",
        secondary="wordparents",
        primaryjoin="Term.id == wordparents.c.WpWoID",
        secondaryjoin="Term.id == wordparents.c.WpParentWoID",
        back_populates="children",
    )
    children = db.relationship(
        "Term",
        secondary="wordparents",
        primaryjoin="Term.id == wordparents.c.WpParentWoID",
        secondaryjoin="Term.id == wordparents.c.WpWoID",
        back_populates="parents",
    )
    images = db.relationship(
        "TermImage",
        back_populates="term",
        lazy="subquery",
        cascade="all, delete-orphan",
    )
    term_flash_message = db.relationship(
        "TermFlashMessage",
        uselist=False,
        back_populates="term",
        cascade="all, delete-orphan",
    )

    def __init__(self, language=None, text=None):
        self.status = 1
        self.translation = None
        self.romanization = None
        self.sync_status = False
        self.term_tags = []
        self.parents = []
        self.children = []
        self.images = []
        if language is not None:
            self.language = language
        if text is not None:
            self.text = text

    @staticmethod
    def create_term_no_parsing(language, text):
        """
        Create a term, but do not reparse it during creation.

        This method is necessary because some parsers return
        different parsed tokens for a given text string based
        on its context.  The general __init__() is used for
        parsing without context, such as creating Terms from
        the UI or during CSV import.  This method is used
        when new terms are created from an already-parsed
        and already-tokenized page of text.
        """
        t = Term()
        t.language = language
        t._text = text  # pylint: disable=protected-access
        t.text_lc = language.get_lowercase(text)
        t.romanization = language.parser.get_reading(text)
        t._calc_token_count()  # pylint: disable=protected-access
        return t

    def __repr__(self):
        return f"<Term {self.id} '{self.text}'>"

    def __eq__(self, other):
        def eqrep(term):
            return f"{term.language.name} {term.text}"

        if isinstance(other, Term):
            return eqrep(self) == eqrep(other)
        return False

    @property
    def text(self):
        "Get the text."
        return self._text

    def _parse_string_add_zws(self, lang, textstring):
        "Parse the string using the language."
        # Clean up encoding cruft.
        t = textstring.strip()
        zws = "\u200B"  # zero-width space
        t = t.replace(zws, "")
        nbsp = "\u00A0"  # non-breaking space
        t = t.replace(nbsp, " ")

        tokens = lang.get_parsed_tokens(t)

        # Terms can't contain paragraph markers.
        tokens = [tok for tok in tokens if tok.token != "¶"]
        tok_strings = [tok.token for tok in tokens]

        t = zws.join(tok_strings)
        return t

    @text.setter
    def text(self, textstring):
        """
        Set the text, textlc, and token count.

        For new terms, just parse, downcase, and get the count.

        For existing terms, ensure that the actual text content has
        not changed.
        """
        if self.language is None:
            raise RuntimeError("Must set term language before setting text")
        lang = self.language

        if self.id is None:
            t = self._parse_string_add_zws(lang, textstring)
            self._text = t
            self.text_lc = lang.get_lowercase(t)
            self.romanization = lang.parser.get_reading(t)
            self._calc_token_count()
        else:
            # new_lc = lang.get_lowercase(textstring)
            # print(f"new lowercase = '{new_lc}', old = '{self.text_lc}'", flush=True)
            if lang.get_lowercase(textstring) != self.text_lc:
                msg = f'Cannot change text of saved term "{self._text}" (id {self.id}).'
                raise TermTextChangedException(msg)
            self._text = textstring

    def _calc_token_count(self):
        "Tokens are separated by zero-width space."
        token_count = 0
        if self._text is not None:
            zws = "\u200B"  # zero-width space
            parts = self._text.split(zws)
            token_count = len(parts)
        self.token_count = token_count

    def remove_all_term_tags(self):
        self.term_tags = []

    def add_term_tag(self, term_tag):
        if term_tag not in self.term_tags:
            self.term_tags.append(term_tag)

    def remove_term_tag(self, term_tag):
        self.term_tags.remove(term_tag)

    def remove_all_parents(self):
        self.parents = []

    def add_parent(self, parent):
        """
        Add valid parent, term cannot be its own parent.
        """
        if self == parent:
            return
        if parent not in self.parents:
            self.parents.append(parent)

    def get_current_image(self, strip_jpeg=True):
        "Get the current (first) image for the term."
        if len(self.images) == 0:
            return None
        i = self.images[0]

        src = i.source

        if not strip_jpeg:
            return src

        # Ugly hack: we have to remove the .jpeg at the end because
        # Flask doesn't handle params with periods.
        return src.replace(".jpeg", "")

    def set_current_image(self, s):
        "Set the current image for this term."
        while len(self.images) > 0:
            self.images.pop(0)
        if (s or "").strip() != "":
            ti = TermImage()
            ti.term = self
            ti.source = s.strip()
            self.images.append(ti)

    @staticmethod
    def delete_empty_images():
        """
        Data clean-up: delete empty images.

        The code was leaving empty images in the db, which are obviously no good.
        This is a hack to clean up the data.
        """
        sql = "delete from wordimages where trim(WiSource) = ''"
        db.session.execute(sqltext(sql))
        db.session.commit()

    def get_flash_message(self):
        "Get the flash message."
        if not self.term_flash_message:
            return None
        return self.term_flash_message.message

    def set_flash_message(self, m):
        "Set a flash message to be shown at some point in the future."
        tfm = self.term_flash_message
        if not tfm:
            tfm = TermFlashMessage()
            self.term_flash_message = tfm
        tfm.message = m

    def pop_flash_message(self):
        "Get the flash message, and remove it from this term."
        if not self.term_flash_message:
            return None
        m = self.term_flash_message.message
        self.term_flash_message = None
        return m

    @staticmethod
    def find(term_id):
        "Get by ID."
        return db.session.query(Term).filter(Term.id == term_id).first()

    @staticmethod
    def find_by_spec(spec):
        """
        Find by the given spec term's language ID and text.
        Returns None if not found.
        """
        langid = spec.language.id
        text_lc = spec.text_lc
        query = db.session.query(Term).filter(
            and_(Term.language_id == langid, Term.text_lc == text_lc)
        )
        terms = query.all()
        if not terms:
            return None
        return terms[0]


class Status:
    """
    Term statuses.
    """

    UNKNOWN = 0
    WELLKNOWN = 99
    IGNORED = 98
