from io import StringIO
import sys
import os
import re
from typing import List
import jaconv
from lute.parse.base import ParsedToken, AbstractParser
from lute.models.setting import UserSetting
from sudachipy import dictionary
import sudachipy


class SudachiParser(AbstractParser):
    """
    Another Japanese Parser, using Sudachi do not need to install MeCab
    https://github.com/WorksApplications/sudachi.rs

    """

    _is_supported = True

    @classmethod
    def is_supported(cls):
        return True

    @classmethod
    def name(cls):
        return "Japanese"

    def get_parsed_tokens(self, text: str, language) -> List[ParsedToken]:
        """
        Parse the string using Sudachi
        """
        text = re.sub(r"[ \t]+", " ", text).strip()
        lines = []
        # ref: https://tdual.hatenablog.com/entry/2020/07/13/162151
        # sudachi has three dicts, core, small, full ,need to be installed by pip
        tokenizer_obj = dictionary.Dictionary(dict="full").create()
        # Split unit: "A" (short), "B" (middle), or "C" (Named Entity) [default: C]
        mode = sudachipy.Tokenizer.SplitMode.C
        for para in text.split("\n"):
            for tok in tokenizer_obj.tokenize(para, mode):
                lines.append(
                    [
                        tok.surface(),
                        tok.part_of_speech()[0],
                        tok.dictionary_id(),
                    ]
                )
            # add the EOP manually
            lines.append(["EOP", "3", "7"])

        def line_to_token(lin):
            "Convert parsed line to a ParsedToken."
            term, node_type, third = lin
            is_eos = term in language.regexp_split_sentences
            if term == "EOP" and third == "7":
                term = "¶"
            # all_word_types=['名詞', '記号', '感動詞', '副詞', '形状詞', '補助記号', '接尾辞', '形容詞', '助詞', '連体詞',
            #        '接続詞', '接頭辞', '代名詞', '動詞']
            word_types = [
                "名詞",
                "形状詞",
                "形容詞",
                "動詞",
                "代名詞",
                "副詞",
                "連体詞",
                "接頭辞",
                "接尾辞",
                "助動詞",
            ]
            is_word = node_type in word_types  # or node_type in "2678"
            return ParsedToken(term, is_word, is_eos)

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
        tokenizer_obj = dictionary.Dictionary(dict="full").create()
        mode = sudachipy.Tokenizer.SplitMode.B
        if self._string_is_hiragana(text):
            return None

        readings = []
        # with MeCab(flags) as nm:
        for tok in tokenizer_obj.tokenize(text, mode):
            readings.append(tok.reading_form())

        # for n in (text, as_nodes=True):
        #     readings.append(n.feature)
        readings = [r.strip() for r in readings if r is not None and r.strip() != ""]

        ret = "".join(readings).strip()
        if ret in ("", text):
            return None

        jp_reading_setting = UserSetting.get_value("japanese_reading")
        if jp_reading_setting == "katakana":
            return ret
        if jp_reading_setting == "hiragana":
            return jaconv.kata2hira(ret)
        if jp_reading_setting == "alphabet":
            return jaconv.kata2alphabet(ret)
        raise RuntimeError(f"Bad reading type {jp_reading_setting}")
