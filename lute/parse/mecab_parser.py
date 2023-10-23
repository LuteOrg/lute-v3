"""
Parsing using MeCab.

Uses natto-py (https://github.com/buruzaemon/natto-py) package and
MeCab to do parsing.

Includes classes:

- JapaneseParser

"""

import re
from typing import List
from natto import MeCab
from lute.parse.base import ParsedToken, AbstractParser


class JapaneseParser(AbstractParser):
    """
    Japanese parser.

    This is only supported if mecab is installed.
    """

    _is_supported = None

    @classmethod
    def is_supported(cls):
        """
        True if a natto MeCab can be instantiated,
        otherwise false.  The value is cached _just in case_,
        thought that's probably premature optimization.
        """
        if JapaneseParser._is_supported is not None:
            return JapaneseParser._is_supported
        b = False
        try:
            MeCab()
            b = True
        except:  # pylint: disable=bare-except
            b = False
        JapaneseParser._is_supported = b
        return b


    @classmethod
    def name(cls):
        return "Japanese"


    def get_parsed_tokens(self, text: str, language) -> List[ParsedToken]:
        "Parse the string using MeCab."
        text = re.sub(r'[ \t]+', ' ', text).strip()

        lines = []
        flags = r'-F %m\t%t\t%h\n -U %m\t%t\t%h\n -E EOP\t3\t7\n'
        with MeCab(flags) as nm:
            for n in nm.parse(text, as_nodes=True):
                lines.append(n.feature)

        lines = [n for n in lines if n is not None]
        lines = [n.strip() for n in lines if n.strip() != '']

        tokens = []
        for lin in lines:
            term, node_type, third = lin.split("\t")
            is_eos = term in language.regexp_split_sentences
            if term == 'EOP' and third == '7':
                term = '¶'
            is_word = node_type in '2678'
            p = ParsedToken(term, is_word, is_eos or term == '¶')
            tokens.append(p)

        return tokens


    # Hiragana is Unicode code block U+3040 - U+309F
    # ref https://stackoverflow.com/questions/72016049/
    #   how-to-check-if-text-is-japanese-hiragana-in-python
    def _char_is_hiragana(self, c) -> bool:
        return '\u3040' <= c <= '\u309F'


    def _string_is_hiragana(self, s: str) -> bool:
        return all(self._char_is_hiragana(c) for c in s)


    def get_reading(self, text: str): # pylint: disable=unused-argument
        """
        Get the pronunciation for the given text.  For most
        languages, this can't be automated.
        """
        if self._string_is_hiragana(text):
            return None

        reading = None
        flags = r'-O yomi'
        with MeCab(flags) as nm:
            for n in nm.parse('必ず', as_nodes=True):
                reading = n.feature
        return reading
