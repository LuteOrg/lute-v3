"""
Language entity.
"""

import re
from sqlalchemy import text, func
from lute.db import db
from lute.parse.registry import get_parser, is_supported


class LanguageDictionary(db.Model):
    """
    Language dictionary.
    """

    __tablename__ = "languagedicts"

    id = db.Column("LdID", db.SmallInteger, primary_key=True)
    language_id = db.Column(
        "LdLgID", db.Integer, db.ForeignKey("languages.LgID"), nullable=False
    )
    language = db.relationship("Language", back_populates="dictionaries")
    usefor = db.Column("LdUseFor", db.String(20), nullable=False)
    dicttype = db.Column("LdType", db.String(20), nullable=False)
    dicturi = db.Column("LdDictURI", db.String(200), nullable=False)
    is_active = db.Column("LdIsActive", db.Boolean, default=True)
    sort_order = db.Column("LdSortOrder", db.SmallInteger, nullable=False)

    # HACK: pre-pend '*' to URLs that need to open a new window.
    # This is a relic of the original code, and should be changed.
    # TODO remove-asterisk-hack: remove * from URL start.
    def make_uri(self):
        "Hack add asterisk."
        prepend = "*" if self.dicttype == "popuphtml" else ""
        return f"{prepend}{self.dicturi}"


class Language(
    db.Model
):  # pylint: disable=too-few-public-methods, too-many-instance-attributes
    """
    Language entity.
    """

    __tablename__ = "languages"

    id = db.Column("LgID", db.SmallInteger, primary_key=True)
    name = db.Column("LgName", db.String(40))

    dictionaries = db.relationship(
        "LanguageDictionary",
        back_populates="language",
        order_by="LanguageDictionary.sort_order",
        lazy="subquery",
        cascade="all, delete-orphan",
    )

    character_substitutions = db.Column("LgCharacterSubstitutions", db.String(500))
    regexp_split_sentences = db.Column("LgRegexpSplitSentences", db.String(500))
    exceptions_split_sentences = db.Column("LgExceptionsSplitSentences", db.String(500))
    _word_characters = db.Column("LgRegexpWordCharacters", db.String(500))
    right_to_left = db.Column("LgRightToLeft", db.Boolean)
    show_romanization = db.Column("LgShowRomanization", db.Boolean)
    parser_type = db.Column("LgParserType", db.String(20))

    def __init__(self):
        self.character_substitutions = "´='|`='|’='|‘='|...=…|..=‥"
        self.regexp_split_sentences = ".!?"
        self.exceptions_split_sentences = "Mr.|Mrs.|Dr.|[A-Z].|Vd.|Vds."
        self.word_characters = "a-zA-ZÀ-ÖØ-öø-ȳáéíóúÁÉÍÓÚñÑ"
        self.right_to_left = False
        self.show_romanization = False
        self.parser_type = "spacedel"
        self.dictionaries = []

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

    def active_dict_uris(self, use_for):
        "Get sorted uris for active dicts of correct type."
        actives = [d for d in self.dictionaries if d.is_active and d.usefor == use_for]
        sorted_actives = sorted(actives, key=lambda x: x.sort_order)
        return [d.make_uri() for d in sorted_actives]

    @property
    def sentence_dict_uris(self):
        return self.active_dict_uris("sentences")

    @classmethod
    def all_dictionaries(cls):
        """
        All dictionaries for all languages.
        """
        lang_dicts = {}
        for lang in Language.query.all():
            lang_dicts[lang.id] = {
                "term": lang.active_dict_uris("terms"),
                "sentence": lang.active_dict_uris("sentences"),
            }
        return lang_dicts

    @staticmethod
    def delete(language):
        """
        Hacky method to delete language and all terms, books, and dicts
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

    def to_dict(self):
        "Return dictionary of data, for serialization."
        ret = {}
        ret["name"] = self.name
        ret["dictionaries"] = []
        for d in self.dictionaries:
            dd = {}
            dd["for"] = d.usefor
            dd["type"] = d.dicttype.replace("html", "")
            dd["url"] = d.dicturi
            dd["active"] = d.is_active
            ret["dictionaries"].append(dd)
        ret["show_romanization"] = self.show_romanization
        ret["right_to_left"] = self.right_to_left
        ret["parser_type"] = self.parser_type
        ret["character_substitutions"] = self.character_substitutions
        ret["split_sentences"] = self.regexp_split_sentences
        ret["split_sentence_exceptions"] = self.exceptions_split_sentences
        ret["word_chars"] = self.word_characters
        return ret

    @staticmethod
    def from_dict(d):
        "Create new Language from dictionary d."

        lang = Language()

        def load(key, method):
            if key in d:
                val = d[key]
                # Handle boolean values
                if isinstance(val, str):
                    temp = val.lower()
                    if temp == "true":
                        val = True
                    elif temp == "false":
                        val = False
                setattr(lang, method, val)

        # Define mappings for fields
        mappings = {
            "name": "name",
            "show_romanization": "show_romanization",
            "right_to_left": "right_to_left",
            "parser_type": "parser_type",
            "character_substitutions": "character_substitutions",
            "split_sentences": "regexp_split_sentences",
            "split_sentence_exceptions": "exceptions_split_sentences",
            "word_chars": "word_characters",
        }

        for key in d.keys():
            funcname = mappings.get(key, "")
            if funcname:
                load(key, funcname)

        ld_sort = 1
        for ld_data in d["dictionaries"]:
            dtype = ld_data["type"]
            if dtype == "embedded":
                dtype = "embeddedhtml"
            elif dtype == "popup":
                dtype = "popuphtml"
            else:
                raise ValueError(f"Invalid dictionary type {dtype}")

            ld = LanguageDictionary()
            # ld.language = lang -- if you do this, the dict is added twice.
            ld.usefor = ld_data["for"]
            ld.dicttype = dtype
            ld.dicturi = ld_data["url"]
            ld.is_active = ld_data.get("active", True)

            ld.sort_order = ld_sort
            ld_sort += 1
            lang.dictionaries.append(ld)

        return lang
