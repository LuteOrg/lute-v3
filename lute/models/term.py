"""
Term entity.
"""

from lute.db import db


wordparents = db.Table(
    'wordparents',
    db.Model.metadata,
    db.Column('WpWoID', db.Integer, db.ForeignKey('words.WoID')),
    db.Column('WpParentWoID', db.Integer, db.ForeignKey('words.WoID'))
)


class TermImage(db.Model):
    "Term images."
    __tablename__ = 'wordimages'

    id = db.Column('WiID', db.Integer, primary_key=True)
    term_id = db.Column('WiWoID', db.Integer, db.ForeignKey('words.WoID'), nullable=False)
    term = db.relationship('Term', back_populates='images')
    source = db.Column('WiSource', db.String(500))


class TermFlashMessage(db.Model):
    "Term flash messages."
    __tablename__ = 'wordflashmessages'

    id = db.Column('WfID', db.Integer, primary_key=True)
    message = db.Column('WfMessage', db.String(200))
    term_id = db.Column(db.Integer, db.ForeignKey('words.WoID'), name='WfWoID', nullable=False)
    term = db.relationship('Term', back_populates='term_flash_message', uselist=False)


wordtags = db.Table(
    'wordtags',
    db.Model.metadata,
    db.Column('WtTgID', db.Integer, db.ForeignKey('tags.TgID')),
    db.Column('WtWoID', db.Integer, db.ForeignKey('words.WoID'))
)


class TermTag(db.Model):
    "Term tags."
    __tablename__ = 'tags'

    id = db.Column('TgID', db.Integer, primary_key=True)
    text = db.Column('TgText', db.String(20))
    _comment = db.Column('TgComment', db.String(200))

    terms = db.relationship('Term', secondary=wordtags, back_populates='term_tags')

    @property
    def comment(self):
        "Comment getter."
        return self._comment

    # TODO tags schema fix: TgComment should be nullable
    # The current schema has the TgComment NOT NULL default '',
    # which was a legacy copy over from LWT. Really, this should
    # be a nullable column, and all blanks should be NULL.
    # Minor change, a nice-to-have.
    @comment.setter
    def comment(self, c):
        "Set cleaned comment."
        self._comment = c if c is not None else ''

    @staticmethod
    def make_term_tag(text, comment=None):
        "Create a TermTag."
        tt = TermTag()
        tt.set_text(text)
        if comment is not None:
            tt.comment(comment)
        return tt


class Term(db.Model): # pylint: disable=too-few-public-methods, too-many-instance-attributes
    """
    Term entity.
    """
    __tablename__ = 'words'

    id = db.Column('WoID', db.SmallInteger, primary_key=True)
    language_id = db.Column('WoLgID', db.Integer, db.ForeignKey('languages.LgID'))

    # Text and TextLC need to be set through setters.
    _text = db.Column('WoText', db.String(250))
    _text_lc = db.Column('WoTextLC', db.String(250))

    status = db.Column('WoStatus', db.Integer)
    translation = db.Column('WoTranslation', db.String(500))
    romanization = db.Column('WoRomanization', db.String(100))
    token_count = db.Column('WoTokenCount', db.Integer)

    language = db.relationship('Language')
    term_tags = db.relationship('TermTag', secondary='wordtags', back_populates='terms')
    parents = db.relationship('Term', secondary='wordparents',
                           primaryjoin='Term.id == wordparents.c.WpWoID',
                           secondaryjoin='Term.id == wordparents.c.WpParentWoID',
                           back_populates='children')
    children = db.relationship('Term', secondary='wordparents',
                            primaryjoin='Term.id == wordparents.c.WpParentWoID',
                            secondaryjoin='Term.id == wordparents.c.WpWoID',
                            back_populates='parents')
    images = db.relationship('TermImage', back_populates='term', lazy='subquery')
    term_flash_message = db.relationship('TermFlashMessage', uselist=False, back_populates='term')

    def __init__(self, language=None, text=None):
        self.status = 1
        self.translation = None
        self.romanization = None
        self.term_tags = []
        self.parents = []
        self.children = []
        self.images = []
        if language is not None:
            self.set_language(language)
        if text is not None:
            self.set_text(text)


    def __repr__(self):
        return f"<Term {self.id} '{self.text}'>"

    @property
    def text(self):
        "Get the text."
        return self._text

    @text.setter
    def text(self, textstring):
        "Set the text, textlc, and token count."
        if self.language is None:
            raise RuntimeError("Must set term language before setting text")

        # Clean up encoding cruft.
        t = textstring.strip()
        zws = '\u200B'  # zero-width space
        t = t.replace(zws, '')
        nbsp = '\u00A0'  # non-breaking space
        t = t.replace(nbsp, ' ')

        lang = self.language
        tokens = lang.get_parsed_tokens(t)

        # Terms can't contain paragraph markers.
        tokens = [tok for tok in tokens if tok.token != "¶"]
        tok_strings = [tok.token for tok in tokens]

        t = zws.join(tok_strings)
        old_text_lc = self._text_lc
        new_text_lc = lang.get_lowercase(t)

        text_changed = old_text_lc is not None and new_text_lc != old_text_lc
        if self.id is not None and text_changed:
            msg = f"Cannot change text of term '{self.text}' (id = {self.id}) once saved."
            raise RuntimeError(msg)

        self._text = t
        self._text_lc = new_text_lc
        self._calc_token_count()

    def _calc_token_count(self):
        "Tokens are separated by zero-width space."
        token_count = 0
        if self._text is not None:
            zws = '\u200B'  # zero-width space
            parts = self._text.split(zws)
            token_count = len(parts)
        self.token_count = token_count

    @property
    def text_lc(self):
        return self._text_lc


    @text_lc.setter
    def text_lc(self, s):
        self._text_lc = s

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
            parent.children.append(self)

    def remove_parent(self, parent):
        "Remove the given parent."
        if parent in self.parents:
            self.parents.remove(parent)
            parent.children.remove(self)

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
        return src.replace('.jpeg', '')

    def set_current_image(self, s):
        "Set the current image for this term."
        if self.images:
            self.images.pop(0)
        if s is not None:
            ti = TermImage()
            ti.set_term(self)
            ti.set_source(s)
            self.images.append(ti)

    # TODO: term dto: where to put dto and conversion methods?
    # def create_term_dto(self):
    #     dto = TermDTO()
    #     dto.id = self.get_id()
    #     dto.language = self.get_language()

    #     t = self.get_text()
    #     zws = '\u200B'  # zero-width space
    #     t = t.replace(zws, '')
    #     dto.OriginalText = t
    #     dto.Text = t

    #     dto.Status = self.get_status()
    #     dto.Translation = self.get_translation()
    #     dto.Romanization = self.get_romanization()
    #     dto.TokenCount = self.get_token_count()
    #     dto.CurrentImage = self.get_current_image()
    #     dto.FlashMessage = self.get_flash_message()

    #     dto.termParents = [p.get_text() for p in self.get_parents()]

    #     if not dto.Romanization:
    #         dto.Romanization = dto.language.get_parser().get_reading(dto.Text)

    #     dto.termTags = [tt.get_text() for tt in self.get_term_tags()]

    #     return dto

    def get_flash_message(self):
        "Get the flash message."
        if not self.term_flash_message:
            return None
        return self.term_flash_message.get_message()

    def set_flash_message(self, m):
        "Set a flash message to be shown at some point in the future."
        tfm = self.term_flash_message
        if not tfm:
            tfm = TermFlashMessage()
            tfm.set_term(self)
            self.term_flash_message = tfm
        tfm.set_message(m)

    def pop_flash_message(self):
        "Get the flash message, and remove it from this term."
        if not self.term_flash_message:
            return None
        m = self.term_flash_message.get_message()
        self.term_flash_message = None
        return m
