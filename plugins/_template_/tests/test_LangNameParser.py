"""
LangNameParser tests.
"""

# TODO fix names, activate tests.

import pytest

# pylint: disable=wrong-import-order
from lute.models.term import Term
from lute.parse.base import ParsedToken

# TODO fix name
from lute_langname_parser.parser import LangNameParser


def test_dummy_test():
    "A dummy test so that pytest doesn't complain in github ci."
    s = "Hello"
    assert s == "Hello", "TODO - fix these tests for your parser :-)"


# TODO activate tests.
def todo_test_token_count(langname):
    """
    token_count checks.
    """
    cases = [
        ("a", 1),
        ("ab", 1),
        ("ac", 2),
        ("ade", 3),
        ("a_longer_check.", 21),
    ]
    for text, expected_count in cases:
        t = Term(langname, text)
        assert t.token_count == expected_count, text
        assert t.text_lc == t.text, "case"


def assert_tokens_equals(text, lang, expected):
    """
    Parsing a text using a language should give the expected parsed tokens.

    expected is given as array of:
    [ original_text, is_word, is_end_of_sentence ]
    """
    p = LangNameParser()
    actual = p.get_parsed_tokens(text, lang)
    expected = [ParsedToken(*a) for a in expected]
    assert [str(a) for a in actual] == [str(e) for e in expected]


def todo_test_end_of_sentence_stored_in_parsed_tokens(langname):
    """
    ParsedToken is marked as EOS=True at ends of sentences.
    """
    s = "some text。More text? Yep."

    expected = [
        ("你好", True),
        ("。", False, True),
        ("吃饭", True),
        ("了", True),
        ("吗", True),
        ("？", False, True),
        ("现在", True),
        ("是", True),
        ("2024", False, False),
        ("年", True),
        ("。", False, True),
    ]
    assert_tokens_equals(s, langname, expected)


def todo_test_carriage_returns_treated_as_reverse_p_character(langname):
    """
    Returns need to be marked with the backwards P for rendering etc.
    """
    s = "some。\ntext。"

    expected = [
        ("你好", True),
        ("。", False, True),
        ("¶", False, True),
        ("现在", True),
        ("。", False, True),
    ]
    assert_tokens_equals(s, mandarin_chinese, expected)


def todo_test_readings():
    """
    Parser returns readings if they add value.
    """
    p = LangNameParser()

    no_reading = ["Hello"]

    for c in no_reading:
        assert p.get_reading(c) is None, c

    cases = [("你好", "nǐ hǎo"), ("欢迎", "huān yíng"), ("中国", "zhōng guó")]

    for c in cases:
        assert p.get_reading(c[0]) == c[1], c[0]
