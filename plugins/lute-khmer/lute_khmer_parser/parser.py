"""
Parsing using khmer-nltk

Includes classes:

- KhmerParser

"""

import re

from typing import List

import khmernltk

from lute.parse.base import ParsedToken, AbstractParser


class KhmerParser(AbstractParser):
    """
    A parser for KHMER
    """

    @classmethod
    def name(cls):
        return "Lute Khmer"

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
        text = text.replace("\n", "NEWLINE_CHARACTER_FOR_LUTE")

        words = khmernltk.word_tokenize(text)  # ... get words using parser.
        tokens = []
        pattern = f"[{language.word_characters}]"
        whitespace_regex = r"[ \t]+"
        for word in words:
            is_end_of_sentence = word in language.regexp_split_sentences
            is_whitespace = re.match(whitespace_regex, word) is not None
            if is_whitespace:
                continue

            is_word_char = (not is_end_of_sentence) and (
                re.match(pattern, word) is not None
            )

            if word == "NEWLINE_CHARACTER_FOR_LUTE":
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
