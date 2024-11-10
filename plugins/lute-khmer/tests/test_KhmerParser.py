"""
KhmerParser tests.
"""


import pytest

# pylint: disable=wrong-import-order
from lute.models.term import Term
from lute.parse.base import ParsedToken

from lute_khmer_parser.parser import KhmerParser


def test_dummy_test():
    "A dummy test so that pytest doesn't complain in github ci."
    s = "Hello"
    assert s == "Hello", "TODO - fix these tests for your parser :-)"


def test_token_count(khmer):
    """
    token_count checks.
    """
    cases = [
        ("ជំរាបសួរ", 2),
        ("ខ្ញុំ", 1),
        ("ខ្ញុំស្រលាញ់អ្នក។", 4),
        ("ខ្ញុំរៀនភាសាខ្មែរ", 4),
        ("ខ្ញុំចូលចិត្តរៀនភាសាខ្មែរជាមួយមិត្តរបស់ខ្ញុំ", 9),
    ]

    for text, expected_count in cases:
        t = Term(khmer, text)
        assert t.token_count == expected_count, text
        assert t.text_lc == t.text, "case"


def assert_tokens_equals(text, lang, expected):
    """
    Parsing a text using a language should give the expected parsed tokens.

    expected is given as array of:
    [ original_text, is_word, is_end_of_sentence ]
    """
    p = KhmerParser()
    actual = p.get_parsed_tokens(text, lang)
    expected = [ParsedToken(*a) for a in expected]
    assert [str(a) for a in actual] == [str(e) for e in expected]


def test_end_of_sentence_stored_in_parsed_tokens(khmer):
    """
    ParsedToken is marked as EOS=True at ends of sentences.
    """
    s = "ខ្ញុំចូលចិត្តរៀនភាសាខ្មែរជាមួយមិត្តរបស់ខ្ញុំ។ ចុះអ្នកវិញ?"

    expected = [
        ("ខ្ញុំ", True),
        ("ចូលចិត្ត", True),
        ("រៀន", True),
        ("ភាសា", True),
        ("ខ្មែរ", True),
        ("ជាមួយ", True),
        ("មិត្ត", True),
        ("របស់", True),
        ("ខ្ញុំ", True),
        ("។", False, True),
        (" ", False),
        ("ចុះ", True),
        ("អ្នក", True),
        ("វិញ", True),
        ("?", False, True),
    ]
    assert_tokens_equals(s, khmer, expected)


def test_carriage_returns_treated_as_reverse_p_character(khmer):
    """
    Returns need to be marked with the backwards P for rendering etc.
    """
    s = "ខ្ញុំចូលចិត្តរៀនភាសាខ្មែរជាមួយមិត្តរបស់ខ្ញុំ។\nចុះអ្នកវិញ?"

    expected = [
        ("ខ្ញុំ", True),
        ("ចូលចិត្ត", True),
        ("រៀន", True),
        ("ភាសា", True),
        ("ខ្មែរ", True),
        ("ជាមួយ", True),
        ("មិត្ត", True),
        ("របស់", True),
        ("ខ្ញុំ", True),
        ("។", False, True),
        ("¶", False, True),
        ("ចុះ", True),
        ("អ្នក", True),
        ("វិញ", True),
        ("?", False, True),
    ]
    assert_tokens_equals(s, khmer, expected)
