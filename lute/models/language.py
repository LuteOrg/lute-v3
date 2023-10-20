"""
Language entity.
"""

import glob
import os
import yaml
from lute.db import db
from lute.parse.registry import get_parser


class Language(db.Model): # pylint: disable=too-few-public-methods, too-many-instance-attributes
    """
    Language entity.
    """

    __tablename__ = 'languages'

    id = db.Column('LgID', db.SmallInteger, primary_key=True)
    name = db.Column('LgName', db.String(40))
    dict_1_uri = db.Column('LgDict1URI', db.String(200))
    dict_2_uri = db.Column('LgDict2URI', db.String(200))
    sentence_translate_uri = db.Column('LgGoogleTranslateURI', db.String(200))
    character_substitutions = db.Column('LgCharacterSubstitutions', db.String(500))
    regexp_split_sentences = db.Column('LgRegexpSplitSentences', db.String(500))
    exceptions_split_sentences = db.Column('LgExceptionsSplitSentences', db.String(500))
    word_characters = db.Column('LgRegexpWordCharacters', db.String(500))
    remove_spaces = db.Column('LgRemoveSpaces', db.Boolean)
    split_each_char = db.Column('LgSplitEachChar', db.Boolean)
    right_to_left = db.Column('LgRightToLeft', db.Boolean)
    show_romanization = db.Column('LgShowRomanization', db.Boolean)
    parser_type = db.Column('LgParserType', db.String(20))


    def __init__(self):
        self.character_substitutions = "´='|`='|’='|‘='|...=…|..=‥"
        self.regexp_split_sentences = '.!?'
        self.exceptions_split_sentences = 'Mr.|Mrs.|Dr.|[A-Z].|Vd.|Vds.'
        self.word_characters = 'a-zA-ZÀ-ÖØ-öø-ȳáéíóúÁÉÍÓÚñÑ'
        self.remove_spaces = False
        self.split_each_char = False
        self.right_to_left = False
        self.show_romanization = False
        self.parser_type = 'spacedel'


    def __repr__(self):
        return f"<Language {self.id} '{self.name}'>"


    @classmethod
    def from_yaml(cls, filename):
        """
        Create a new Language object from a yaml definition.
        """
        with open(filename, 'r', encoding='utf-8') as file:
            d = yaml.safe_load(file)

        lang = cls()

        def load(key, method):
            if key in d:
                val = d[key]
                # Handle boolean values
                if isinstance(val, str):
                    temp = val.lower()
                    if temp == 'true':
                        val = True
                    elif temp == 'false':
                        val = False
                setattr(lang, method, val)

        # Define mappings for fields
        mappings = {
            'name': 'name',
            'dict_1': 'dict_1_uri',
            'dict_2': 'dict_2_uri',
            'sentence_translation': 'sentence_translate_uri',
            'show_romanization': 'show_romanization',
            'right_to_left': 'right_to_left',
            'parser_type': 'parser_type',
            'character_substitutions': 'character_substitutions',
            'split_sentences': 'regexp_split_sentences',
            'split_sentence_exceptions': 'exceptions_split_sentences',
            'word_chars': 'word_characters',
        }

        for key in d.keys():
            funcname = mappings.get(key, '')
            if funcname:
                load(key, funcname)

        return lang


    @classmethod
    def get_predefined(cls):
        """
        Return languages that have yaml definitions in demo/languages.
        """
        current_dir = os.path.dirname(__file__)
        demoglob = os.path.join(current_dir, '../../demo/languages/*.yaml')
        ret = [Language.from_yaml(f) for f in glob.glob(demoglob)]

        # TODO mecab: remove japanese if no mecab
        # no_mecab = not JapaneseParser.mecab_installed()
        # if no_mecab:
        #    ret = [lang for lang in ret if lang.get_lg_parser_type() != 'japanese']

        ret.sort(key=lambda x: x.name)
        return ret


    # TODO language relationships: should deleting lang should delete books and terms
    # books = db.relationship('Book', backref='language', lazy='extra')
    # terms = db.relationship('Term', backref='language', lazy='extra')


    @property
    def parser(self):
        return get_parser(self.parser_type)

    def get_parsed_tokens(self, s):
        return self.parser.get_parsed_tokens(s, self)

    def get_lowercase(self, s) -> str:
        return self.parser.get_lowercase(s)


    @staticmethod
    def find(language_id):
        "Get by ID."
        return db.session.query(Language).filter(Language.id == language_id).first()
