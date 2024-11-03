"""
ThaiParser tests.
"""


import pytest

# pylint: disable=wrong-import-order
from lute.models.term import Term
from lute.parse.base import ParsedToken

from lute_thai_parser.parser import ThaiParser


def test_token_count(thai):
    """
    token_count checks.
    """
    cases = [
        ("สวัสดี", 1),
        ("ลาก่อน", 1),
        ("ฉันรักคุณ", 3),
        ("ฉันกำลังเรียนภาษาไทย", 4),
    ]
    for text, expected_count in cases:
        t = Term(thai, text)
        assert t.token_count == expected_count, text
        assert t.text_lc == t.text, "case"


def assert_tokens_equals(text, lang, expected):
    """
    Parsing a text using a language should give the expected parsed tokens.

    expected is given as array of:
    [ original_text, is_word, is_end_of_sentence ]
    """
    p = ThaiParser()
    actual = p.get_parsed_tokens(text, lang)
    expected = [ParsedToken(*a) for a in expected]
    assert [str(a) for a in actual] == [str(e) for e in expected]


def test_end_of_sentence_stored_in_parsed_tokens(thai):
    """
    ParsedToken is marked as EOS=True at ends of sentences.
    """
    s = "สวัสดีทุกคน! ฉันเรียนภาษาไทยมา2เดือนแล้วฯ"

    expected = [
        ("สวัสดี", True),
        ("ทุกคน", True),
        ("!", False, True),
        (" ", False, True),
        ("ฉัน", True),
        ("เรียน", True),
        ("ภาษาไทย", True),
        ("มา", True),
        ("2", False),
        ("เดือน", True),
        ("แล้ว", True, False),
        ("ฯ", False, True),
    ]
    assert_tokens_equals(s, thai, expected)


def test_carriage_returns_treated_as_reverse_p_character(thai):
    """
    Returns need to be marked with the backwards P for rendering etc.
    """
    s = "สวัสดีทุกคน!\nฉันเรียนภาษาไทยมา2เดือนแล้ว"

    expected = [
        ("สวัสดี", True),
        ("ทุกคน", True),
        ("!", False, True),
        ("¶", False, True),
        ("ฉัน", True),
        ("เรียน", True),
        ("ภาษาไทย", True),
        ("มา", True),
        ("2", False),
        ("เดือน", True),
        ("แล้ว", True, False),
    ]
    assert_tokens_equals(s, thai, expected)
