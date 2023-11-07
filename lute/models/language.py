"""
Language entity.
"""

import re
from sqlalchemy import text, func
from lute.db import db
from lute.parse.registry import get_parser, is_supported


class Language(
    db.Model
):  # pylint: disable=too-few-public-methods, too-many-instance-attributes
    """
    Language entity.
    """

    __tablename__ = "languages"

    id = db.Column("LgID", db.SmallInteger, primary_key=True)
    name = db.Column("LgName", db.String(40))
    dict_1_uri = db.Column("LgDict1URI", db.String(200))
    dict_2_uri = db.Column("LgDict2URI", db.String(200))
    sentence_translate_uri = db.Column("LgGoogleTranslateURI", db.String(200))
    character_substitutions = db.Column("LgCharacterSubstitutions", db.String(500))
    regexp_split_sentences = db.Column("LgRegexpSplitSentences", db.String(500))
    exceptions_split_sentences = db.Column("LgExceptionsSplitSentences", db.String(500))
    _word_characters = db.Column("LgRegexpWordCharacters", db.String(500))
    remove_spaces = db.Column("LgRemoveSpaces", db.Boolean)
    split_each_char = db.Column("LgSplitEachChar", db.Boolean)
    right_to_left = db.Column("LgRightToLeft", db.Boolean)
    show_romanization = db.Column("LgShowRomanization", db.Boolean)
    parser_type = db.Column("LgParserType", db.String(20))

    def __init__(self):
        self.character_substitutions = "´='|`='|’='|‘='|...=…|..=‥"
        self.regexp_split_sentences = ".!?"
        self.exceptions_split_sentences = "Mr.|Mrs.|Dr.|[A-Z].|Vd.|Vds."
        self.word_characters = "a-zA-ZÀ-ÖØ-öø-ȳáéíóúÁÉÍÓÚñÑ"
        self.remove_spaces = False
        self.split_each_char = False
        self.right_to_left = False
        self.show_romanization = False
        self.parser_type = "spacedel"

    def __repr__(self):
        return f"<Language {self.id} '{self.name}'>"

    def _get_python_regex_pattern(self, s):
        """
        Old Lute v2 ran in php, so the language word chars regex
        could look like this:

        x{0600}-x{06FF}x{FE70}-x{FEFC}  (where x = backslash-x)

        This needs to be converted to the python equivalent, e.g.

        u0600-u06FFuFE70-uFEFC  (where u = backslash-u)
        """

        def convert_match(match):
            # Convert backslash-x{XXXX} to backslash-uXXXX
            hex_value = match.group(1)
            return f"\\u{hex_value}"

        ret = re.sub(r"\\x{([0-9A-Fa-f]+)}", convert_match, s)
        return ret

    @property
    def word_characters(self):
        return self._get_python_regex_pattern(self._word_characters)

    @word_characters.setter
    def word_characters(self, s):
        self._word_characters = self._get_python_regex_pattern(s)

    @classmethod
    def all_dictionaries(cls):
        """
        All dictionaries for all languages.
        """
        languages = Language.query.all()
        language_data = {}
        for language in languages:
            term_dicts = [language.dict_1_uri, language.dict_2_uri]
            term_dicts = [uri for uri in term_dicts if uri is not None]

            data = {"term": term_dicts, "sentence": language.sentence_translate_uri}

            language_data[language.id] = data
        return language_data

    @staticmethod
    def delete(language):
        """
        Hacky method to delete language and all terms and books
        associated with it.

        There is _certainly_ a better way to do this using
        Sqlalchemy relationships and cascade deletes, but I
        was running into problems with it (things not cascading,
        or warnings ("SAWarning: Object of type <Term> not in
        session, add operation along 'Language.terms' will not
        proceed") during test runs.  It would be nice to have
        a "correct" mapping, but this is good enough for now.

        TODO zzfuture fix: fix Language-Book and -Term mappings.
        """
        sqls = [
            "pragma foreign_keys = ON",
            f"delete from languages where LgID = {language.id}",
        ]
        for s in sqls:
            db.session.execute(text(s))
        db.session.commit()

    @property
    def parser(self):
        return get_parser(self.parser_type)

    @property
    def is_supported(self):
        "True if the language's parser is supported."
        return is_supported(self.parser_type)

    def get_parsed_tokens(self, s):
        return self.parser.get_parsed_tokens(s, self)

    def get_lowercase(self, s) -> str:
        return self.parser.get_lowercase(s)

    @staticmethod
    def find(language_id):
        "Get by ID."
        return db.session.query(Language).filter(Language.id == language_id).first()

    @staticmethod
    def find_by_name(name):
        "Get by name."
        return (
            db.session.query(Language)
            .filter(func.lower(Language.name) == func.lower(name))
            .first()
        )
