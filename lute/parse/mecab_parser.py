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
import jaconv
from lute.parse.base import ParsedToken, AbstractParser
from lute.models.setting import UserSetting, MissingUserSettingKeyException


class JapaneseParser(AbstractParser):
    """
    Japanese parser.

    This is only supported if mecab is installed.

    The parser uses natto-py library, and so should
    be able to find mecab automatically; if it can't,
    you may need to set the MECAB_PATH env variable,
    managed by UserSetting.set_value("mecab_path", p)
    """

    _is_supported = None
    _old_mecab_path = None

    @classmethod
    def is_supported(cls):
        """
        True if a natto MeCab can be instantiated,
        otherwise false.
        """
        mecab_path = os.environ.get("MECAB_PATH", "<NOTSET>")
        if (
            mecab_path == JapaneseParser._old_mecab_path
        ) and JapaneseParser._is_supported is not None:
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

        JapaneseParser._old_mecab_path = mecab_path
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

        lines = [
            n.strip().split("\t") for n in lines if n is not None and n.strip() != ""
        ]

        # Production bug: JP parsing with MeCab would sometimes return a line
        # "0\t4" before an end-of-paragraph "EOP\t3\t7", reasons unknown.  These
        # "0\t4" tokens don't have any function, and cause problems in subsequent
        # steps of the processing in line_to_token(), so just remove them.
        lines = [n for n in lines if len(n) == 3]

        def line_to_token(lin):
            "Convert parsed line to a ParsedToken."
            term, node_type, third = lin
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

        jp_reading_setting = ""
        try:
            jp_reading_setting = UserSetting.get_value("japanese_reading")
        except MissingUserSettingKeyException:
            # During loading of demo data, the key isn't set, but the
            # reading isn't needed either, as this is only called when
            # calculating stats.
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

        if jp_reading_setting == "katakana":
            return ret
        if jp_reading_setting == "hiragana":
            return jaconv.kata2hira(ret)
        if jp_reading_setting == "alphabet":
            return jaconv.kata2alphabet(ret)
        raise RuntimeError(f"Bad reading type {jp_reading_setting}")
