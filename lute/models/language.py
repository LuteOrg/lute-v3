"""
Language entity.
"""

from lute.db import db

class Language(db.Model): # pylint: disable=too-few-public-methods
    """
    Language entity.
    """

    __tablename__ = 'languages'

    id = db.Column('LgID', db.SmallInteger, primary_key=True)
    name = db.Column('LgName', db.String(40))
    dict_1_uri = db.Column('LgDict1URI', db.String(200))
    dict_2_uri = db.Column('LgDict2URI', db.String(200))
    sentence_translate_uri = db.Column('LgGoogleTranslateURI', db.String(200))
    character_substitutions = db.Column(
        'LgCharacterSubstitutions', db.String(500),
        default="´='|`='|’='|‘='|...=…|..=‥")
    regexp_split_sentences = db.Column(
        'LgRegexpSplitSentences', db.String(500),
        default='.!?')
    exceptions_split_sentences = db.Column(
        'LgExceptionsSplitSentences', db.String(500),
        default='Mr.|Mrs.|Dr.|[A-Z].|Vd.|Vds.')
    word_characters = db.Column(
        'LgRegexpWordCharacters', db.String(500),
        default='a-zA-ZÀ-ÖØ-öø-ȳáéíóúÁÉÍÓÚñÑ')
    remove_spaces = db.Column('LgRemoveSpaces', db.Boolean, default=False)
    split_each_char = db.Column('LgSplitEachChar', db.Boolean, default=False)
    right_to_left = db.Column('LgRightToLeft', db.Boolean, default=False)
    show_romanization = db.Column('LgShowRomanization', db.Boolean, default=False)
    parser_type = db.Column('LgParserType', db.String(20), default='spacedel')

    # relationships.
    # books = db.relationship('Book', backref='language', lazy='extra')
    # terms = db.relationship('Term', backref='language', lazy='extra')
