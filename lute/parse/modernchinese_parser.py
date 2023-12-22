"""
Parsing modern chinese with hanlp,
which requires PyTorch、TensorFlow, so it's not supported by default until installed hanlp by pip.
https://github.com/hankcs/HanLP/tree/master
about the model path configuration
https://hanlp.hankcs.com/docs/configure.html

If hanlp is not installed, using pkuseg instead
"""
from typing import List
from functools import lru_cache

from lute.parse.base import AbstractParser
from lute.parse.base import ParsedToken
import pkuseg

CHINESE_PUNCTUATIONS = (
    r"！？｡。＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､、〃》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘’‛“”„‟…‧﹏.\n"
)


class ModernChineseParser(AbstractParser):
    """
    Using hanlp for parsing modern Chinese,
    if the user don't install hanlp, the parser is not supported.
    https://github.com/hankcs/HanLP/blob/doc-zh/plugins/hanlp_demo/hanlp_demo/zh/tok_stl.ipynb
    """

    _seg = None

    @classmethod
    @lru_cache()
    def is_supported(cls):
        """
        Using lru_cache to make the test execution run fast,
        otherwise the test execution will run very slowly,
        the process of checking whether the hanlp package is installed can be slow.
        If hanlp is not installed, using pkuseg as default chinese parser.
        """
        _res = True
        try:
            import hanlp

            ModernChineseParser._seg = hanlp.load(
                hanlp.pretrained.tok.FINE_ELECTRA_SMALL_ZH
            )
        except ImportError as _:
            _pkuseg = pkuseg.pkuseg()
            ModernChineseParser._seg = _pkuseg.cut

        return _res

    @classmethod
    def name(cls):
        return "ModernChinese"

    @lru_cache()
    def parse_para(self, para_text):
        """
        Parsing the paragraph using hanlp
        """
        para_result = []
        for tok in ModernChineseParser._seg(para_text):
            is_word = tok not in CHINESE_PUNCTUATIONS
            para_result.append((tok, is_word))
        return para_result

    @lru_cache()
    def get_parsed_tokens(self, text: str, language) -> List:
        """
        Parsing the text by paragraph, then generate the ParsedToken List,
        for the correct token order.
        cached the parsed result
        """
        tokens = []
        for para in text.split("\n"):
            para = para.strip()
            tokens.extend(self.parse_para(para))
            tokens.append(["¶", False])
        # Remove the trailing ¶
        # by stripping it from the result
        tokens.pop()

        return [ParsedToken(tok, is_word, tok == "¶") for tok, is_word in tokens]
