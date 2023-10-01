"""
Language entity.
"""

from lute.db import db

class Language(db.Model): # pylint: disable=too-few-public-methods
    """
    Language entity.
    """

    __tablename__ = 'languages'

    LgID = db.Column(db.SmallInteger, primary_key=True)
    LgName = db.Column(db.String(40))
    LgDict1URI = db.Column(db.String(200))
    LgDict2URI = db.Column(db.String(200))
    LgGoogleTranslateURI = db.Column(db.String(200))
    LgCharacterSubstitutions = db.Column(db.String(500), default="´='|`='|’='|‘='|...=…|..=‥")
    LgRegexpSplitSentences = db.Column(db.String(500), default='.!?')
    LgExceptionsSplitSentences = db.Column(db.String(500), default='Mr.|Mrs.|Dr.|[A-Z].|Vd.|Vds.')
    LgRegexpWordCharacters = db.Column(db.String(500), default='a-zA-ZÀ-ÖØ-öø-ȳáéíóúÁÉÍÓÚñÑ')
    LgRemoveSpaces = db.Column(db.Boolean, default=False)
    LgSplitEachChar = db.Column(db.Boolean, default=False)
    LgRightToLeft = db.Column(db.Boolean, default=False)
    LgShowRomanization = db.Column(db.Boolean, default=False)
    LgParserType = db.Column(db.String(20), default='spacedel')

    # relationships.
    # books = db.relationship('Book', backref='language', lazy='extra')
    # terms = db.relationship('Term', backref='language', lazy='extra')
