"""
Parsing for single-character languages.

The parser uses some Language settings (e.g., word characters) to
perform the actual parsing.

Includes classes:

- ClassicalChineseParser

"""

import re
from typing import List
from lute.parse.base import ParsedToken, AbstractParser


class ClassicalChineseParser(AbstractParser):
    """
    A general parser for space-delimited languages,
    such as English, French, Spanish ... etc.
    """

    @classmethod
    def name(cls):
        return "Classical Chinese"

    def get_parsed_tokens(self, text: str, language) -> List[ParsedToken]:
        """
        Returns ParsedToken array for given language.
        """
        text = re.sub(r"[ \t]+", "", text)

        replacements = language.character_substitutions.split("|")
        for replacement in replacements:
            fromto = replacement.strip().split("=")
            if len(fromto) >= 2:
                rfrom = fromto[0].strip()
                rto = fromto[1].strip()
                text = text.replace(rfrom, rto)

        text = text.replace("\r\n", "\n")
        text = text.replace("{", "[")
        text = text.replace("}", "]")
        text = text.replace("\n", "¶")
        text = text.strip()

        tokens = []
        pattern = f"[{language.word_characters}]"
        for char in text:
            is_word_char = re.match(pattern, char) is not None
            is_end_of_sentence = char in language.regexp_split_sentences
            if char == "¶":
                is_end_of_sentence = True
            p = ParsedToken(char, is_word_char, is_end_of_sentence)
            tokens.append(p)

        return tokens
