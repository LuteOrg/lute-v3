"""
Parsing using Jieba

The parser uses jieba to do parsing and pypinyin for character readings

Includes classes:

- MandarinParser

"""

import re
import os
from typing import List
import jieba
from pypinyin import pinyin
from lute.parse.base import ParsedToken, AbstractParser


class MandarinParser(AbstractParser):
    """
    A parser for Mandarin Chinese,
    using the jieba library for text segmentation.

    The user can add some exceptions to the "parsing_exceptions.txt"
    data file.
    """

    @classmethod
    def name(cls):
        return "Lute Mandarin Chinese"

    @classmethod
    def uses_data_directory(cls):
        "Uses the data_directory (defined in the AbstractParser)."
        return True

    @classmethod
    def parser_exceptions_file(cls):
        """Full path to an exceptions file (in the parser's
        data_directory) to indicate which terms should be broken up
        differently than what jieba suggests.  For example, jieba
        parses "清华大学" as a single token; however the user can
        specify different parsing for this group:

        "清华,大学" says "parse 清华大学 into two tokens, 清华/大学."
        "清,华,大学" says "parse 清华大学 into three tokens, 清/华/大学."

        Each rule is placed on a separate line in the
        parser_exceptions file, e.g, the following file content
        defines two rules:

        清华,大学
        学,华,大
        """
        return os.path.join(cls.data_directory, "parser_exceptions.txt")

    @classmethod
    def init_data_directory(cls):
        "Set up necessary files."
        fp = cls.parser_exceptions_file()
        if not os.path.exists(fp):
            with open(fp, "w", encoding="utf8") as f:
                f.write("# Parsing exceptions.")
                f.write("# Place each rule on a separate line.")
                f.write("# e.g.:")
                f.write("# 清华,大学")
                f.write("# Lines preceded with # are ignored.")

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
