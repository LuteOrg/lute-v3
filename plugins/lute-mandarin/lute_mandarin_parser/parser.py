"""
Parsing using Jieba

The parser uses jieba to do parsing and pypinyin for character readings

Includes classes:

- MandarinParser

"""

import re
from typing import List
import jieba
from pypinyin import pinyin
from lute.parse.base import ParsedToken, AbstractParser


class MandarinParser(AbstractParser):
    """
    A parser for Mandarin Chinese,
    using the jieba library for text segmentation.
    """

    @classmethod
    def name(cls):
        return "Lute Mandarin Chinese"

    def get_parsed_tokens(self, text: str, language) -> List[ParsedToken]:
        """
        Returns ParsedToken array for given language.
        """

        # Ensure standard carriage returns so that paragraph
        # markers are used correctly.  Lute uses paragraph markers
        # for rendering.
        text = text.replace("\r\n", "\n")

        words = list(jieba.cut(text))
        tokens = []
        pattern = f"[{language.word_characters}]"
        for word in words:
            is_word_char = re.match(pattern, word) is not None
            is_end_of_sentence = word in language.regexp_split_sentences
            if word == "\n":
                word = "¶"
            if word == "¶":
                is_word_char = False
                is_end_of_sentence = True
            p = ParsedToken(word, is_word_char, is_end_of_sentence)
            tokens.append(p)
        return tokens

    def get_reading(self, text: str):
        """
        Get the pinyin for the given text.
        Returns None if the text is all Chinese characters, or the pinyin
        doesn't add value (same as text).
        """
        # Use pypinyin to get the pinyin of the text
        pinyin_list = pinyin(text)
        # Flatten the list of lists to a single list
        pinyin_list = (item for sublist in pinyin_list for item in sublist)
        # Join the pinyin into a single string
        ret = " ".join(pinyin_list)
        if ret in ("", text):
            return None
        return ret
