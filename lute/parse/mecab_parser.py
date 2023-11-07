"""
Parsing using MeCab.

Uses natto-py (https://github.com/buruzaemon/natto-py) package and
MeCab to do parsing.

Includes classes:

- JapaneseParser

"""

from io import StringIO
import sys
import os
import re
from typing import List
from natto import MeCab
from lute.parse.base import ParsedToken, AbstractParser


class JapaneseParser(AbstractParser):
    """
    Japanese parser.

    This is only supported if mecab is installed.

    The parser uses natto-py library, and so should
    be able to find mecab automatically; if it can't,
    you may need to set the MECAB_PATH env variable,
    managed here by the set_mecab_path_envkey() method.
    """

    _is_supported = None

    @staticmethod
    def set_mecab_path_envkey(v):
        """
        Sets the key MECAB_PATH key for natto-py.
        Deletes if None or ''.
        """
        if "MECAB_PATH" in os.environ:
            del os.environ["MECAB_PATH"]
        if v is not None and v.strip() != "":
            os.environ["MECAB_PATH"] = v.strip()
        JapaneseParser._is_supported = None

    @staticmethod
    def get_mecab_path_envkey():
        return os.getenv("MECAB_PATH")

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

        # Calling MeCab() prints to stderr even if the
        # exception is caught.  Suppress that output noise.
        temp_err = StringIO()
        try:
            sys.stderr = temp_err
            MeCab()
            b = True
        except:  # pylint: disable=bare-except
            b = False
        finally:
            sys.stderr = sys.__stderr__

        JapaneseParser._is_supported = b
        return b

    @classmethod
    def name(cls):
        return "Japanese"

    def get_parsed_tokens(self, text: str, language) -> List[ParsedToken]:
        "Parse the string using MeCab."
        text = re.sub(r"[ \t]+", " ", text).strip()

        lines = []

        # If the string contains a "\n", MeCab appears to silently
        # remove it.  Splitting it works (ref test_JapaneseParser).
        # Flags: ref https://github.com/buruzaemon/natto-py:
        #    -F = node format
        #    -U = unknown format
        #    -E = EOP format
        with MeCab(r"-F %m\t%t\t%h\n -U %m\t%t\t%h\n -E EOP\t3\t7\n") as nm:
            for para in text.split("\n"):
                for n in nm.parse(para, as_nodes=True):
                    lines.append(n.feature)

        lines = [n.strip() for n in lines if n is not None and n.strip() != ""]

        def line_to_token(lin):
            "Convert parsed line to a ParsedToken."
            term, node_type, third = lin.split("\t")
            is_eos = term in language.regexp_split_sentences
            if term == "EOP" and third == "7":
                term = "¶"
            is_word = node_type in "2678"
            return ParsedToken(term, is_word, is_eos or term == "¶")

        tokens = [line_to_token(lin) for lin in lines]
        return tokens

    # Hiragana is Unicode code block U+3040 - U+309F
    # ref https://stackoverflow.com/questions/72016049/
    #   how-to-check-if-text-is-japanese-hiragana-in-python
    def _char_is_hiragana(self, c) -> bool:
        return "\u3040" <= c <= "\u309F"

    def _string_is_hiragana(self, s: str) -> bool:
        return all(self._char_is_hiragana(c) for c in s)

    def get_reading(self, text: str):
        """
        Get the pronunciation for the given text.

        Returns None if the text is all hiragana, or the pronunciation
        doesn't add value (same as text).
        """
        if self._string_is_hiragana(text):
            return None

        flags = r"-O yomi"
        readings = []
        with MeCab(flags) as nm:
            for n in nm.parse(text, as_nodes=True):
                readings.append(n.feature)
        readings = [r.strip() for r in readings if r is not None and r.strip() != ""]

        ret = "".join(readings).strip()
        if ret in ("", text):
            return None
        return ret
