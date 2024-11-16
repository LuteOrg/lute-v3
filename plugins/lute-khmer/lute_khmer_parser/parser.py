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

    def _handle_special_token(self, token: str, special_char: str) -> List[str]:
        """
        Handle special token scenarios by replacing all special tokens with newline characters.

        Example:
            If \ is the special token then
            "\hey\man\\\" will evaluate as
            ["\n", "hey", "\n", "man", "\n", "\n", "\n"]
        """
        if token == special_char:
            return ["\n"]

        num_leading_slashes = len(token) - len(token.lstrip(special_char))
        num_trailing_slashes = len(token) - len(token.rstrip(special_char))
        output = []

        output.extend("\n" * num_leading_slashes)

        tokens = token.strip(special_char).split(special_char)

        if len(tokens) == 1:
            output.append(tokens[0])
        else:
            for token in tokens[:-1]:
                output.append(token)
                output.append("\n")
            output.append(tokens[-1])

        output.extend("\n" * num_trailing_slashes)

        return output

    def word_tokenize(self, text: str) -> List[str]:
        """
        Tokenize a text using khmernltk and handle the fact that khmernltk
        completely omits newline characters by replacing all newline chars with
        something that khmernltk won't omit.
        """
        special_char = "\\"
        text = text.replace("\n", special_char)
        output = []

        for token in khmernltk.word_tokenize(text):
            if special_char in token:
                output.extend(self._handle_special_token(token, special_char))
                continue
            output.append(token)
        return output

    def get_parsed_tokens(self, text: str, language) -> List[ParsedToken]:
        """
        Returns ParsedToken array for given language.
        """

        # Ensure standard carriage returns so that paragraph
        # markers are used correctly.  Lute uses paragraph markers
        # for rendering.
        text = text.replace("\r\n", "\n")
        words = self.word_tokenize(text)  # ... get words using parser.
        pattern = f"[{language.word_characters}]"
        tokens = []
        for word in words:
            is_end_of_sentence = word in language.regexp_split_sentences
            is_word_char = (not is_end_of_sentence) and (
                re.match(pattern, word) is not None
            )
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
