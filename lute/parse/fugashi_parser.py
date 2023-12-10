import re
from typing import List
import jaconv
from lute.parse.base import ParsedToken, AbstractParser
from lute.models.setting import UserSetting
from fugashi import Tagger


class FugashiParser(AbstractParser):
    """
    Another Japanese Parser, Fugashi which provide wheels for
    Linux, OSX and Win64, not suitable for Win32, can easy using the UniDic
    https://github.com/polm/fugashi
    https://clrd.ninjal.ac.jp/unidic/
    """

    _is_supported = True
    _dict_path = ""
    # Can using -d <dict_path> to using the local unidic, 
    # For example 
    # _tagger = Tagger("-d /home/fy/.unidics/unidic-csj-202302")
    # unidic can download from  https://clrd.ninjal.ac.jp/unidic/
    _tagger = Tagger()
    _cache = {}

    @classmethod
    def is_supported(cls):
        return True

    @classmethod
    def name(cls):
        return "Japanese"

    @classmethod
    def _get_cache(cls, key):
        return FugashiParser._cache.get(key)

    @classmethod
    def _set_cache(cls, key, res):
        FugashiParser._cache[key] = res

    @classmethod
    def parse_para(cls, text: str, language) -> List[List[str]]:
        lines = []


        if FugashiParser._get_cache(text):
            return FugashiParser._get_cache(text)
        for tok in FugashiParser._tagger(text):
            lines.append(
                [
                    tok.surface,
                    str(tok.char_type),
                    "-1" if tok.is_unk else "0"
                ]
            )
        lines.append(["EOP", "3", "7"])
        # res = [line_to_token(lin) for lin in lines]

        FugashiParser._set_cache(text, lines)
        return lines

    def get_parsed_tokens(self, text: str, language) -> List[ParsedToken]:
        """
        Parse the string using Sudachi
        """
        text = re.sub(r"[ \t]+", " ", text).strip()
        tokens = []
        lines = []
        def line_to_token(lin):
            "Convert parsed line to a ParsedToken."
            term, node_type, third = lin
            is_eos = term in language.regexp_split_sentences
            if term == "EOP" and third == "7":
                term = "¶"
            is_word = (
                node_type in "2678" and third !='-1'
            )  # or node_type in "2678"
            return ParsedToken(term, is_word, is_eos)

        # ref: https://tdual.hatenablog.com/entry/2020/07/13/162151
        # sudachi has three dicts, core, small, full ,need to be installed by pip
        # Split unit: "A" (short), "B" (middle), or "C" (Named Entity) [default: C]
        for para in text.split("\n"):
            lines.extend(FugashiParser.parse_para(para, language))

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

        readings = []
        # with MeCab(flags) as nm:
        for tok in FugashiParser._tagger(text):
            readings.append(tok.feature.kana)

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
