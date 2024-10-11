"""
Parsing using TODO

Includes classes:

- LangNameParser

"""

import re
from typing import List
from lute.parse.base import ParsedToken, AbstractParser


# TODO fix names
class LangNameParser(AbstractParser):
    """
    A parser for LANGNAME
    """

    @classmethod
    def name(cls):
        return "Lute LangName"

    @classmethod
    def uses_data_directory(cls):
        "Uses the data_directory (defined in the AbstractParser)."
        return False  # or True

    # @classmethod
    # def init_data_directory(cls):
    #     "Set up necessary files."
    #     pass

    def get_parsed_tokens(self, text: str, language) -> List[ParsedToken]:
        """
        Returns ParsedToken array for given language.
        """

        # Ensure standard carriage returns so that paragraph
        # markers are used correctly.  Lute uses paragraph markers
        # for rendering.
        text = text.replace("\r\n", "\n")

        words = []  # ... get words using parser.
        tokens = []
        pattern = f"[{language.word_characters}]"
        for word in words:
            is_word_char = re.match(pattern, word) is not None
            is_end_of_sentence = word in language.regexp_split_sentences
            if word == "\n":
                word = "¶"
            if word == "¶":
                is_word_char = False
                is_end_of_sentence = True
            t = ParsedToken(word, is_word_char, is_end_of_sentence)
            tokens.append(t)
        return tokens

    def get_reading(self, text: str):
        """
        Get reading -- some parsers can return readings.
        """
        return None
