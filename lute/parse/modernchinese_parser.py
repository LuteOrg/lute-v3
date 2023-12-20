from typing import List
from lute.parse.base import AbstractParser
from lute.parse.base import ParsedToken
from functools import lru_cache
import pkuseg

# Chinese Punctuation using to determine if a token is a word.
CHINESE_PUNCTUATIONS = (
    r"！？｡＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､、〃》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘’‛“”„‟…‧﹏.\n"
)


class ModernChineseParser(AbstractParser):
    """
    Using pkuseg to parsing the chinese
    https://github.com/lancopku/pkuseg-python
    """

    _seg = pkuseg.pkuseg()

    @classmethod
    def name(cls):
        return "ModernChinese"

    @lru_cache()
    def _parse_para(self, para_text):
        para_result = []
        for tok in ModernChineseParser._seg.cut(para_text):
            is_word = tok not in CHINESE_PUNCTUATIONS
            para_result.append((tok, is_word))
        return para_result

    @lru_cache()
    def get_parsed_tokens(self, text: str, language) -> List:
        """
        using lru_cache for caching the parsed result
        """
        tokens = []
        for para in text.split("\n"):
            para = para.strip()
            tokens.extend(self._parse_para(para))
            tokens.append(["¶", False])

        return [ParsedToken(tok, is_word, tok == "¶") for tok, is_word in tokens]
