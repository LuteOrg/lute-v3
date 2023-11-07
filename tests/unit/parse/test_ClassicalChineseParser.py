"""
JapaneseParser tests.
"""

from lute.parse.base import ParsedToken


def assert_tokens_equals(text, lang, expected):
    """
    Parsing a text using a language should give the expected parsed tokens.

    expected is given as array of:
    [ original_text, is_word, is_end_of_sentence ]
    """
    p = lang.parser
    print("passing text:")
    print(text)
    actual = p.get_parsed_tokens(text, lang)
    expected = [ParsedToken(*a) for a in expected]
    assert [str(a) for a in actual] == [str(e) for e in expected]


def test_sample_1(classical_chinese):
    "Sample text parsed."
    s = "學而時習之，不亦說乎？"

    expected = [
        ["學", True],
        ["而", True],
        ["時", True],
        ["習", True],
        ["之", True],
        ["，", False],
        ["不", True],
        ["亦", True],
        ["說", True],
        ["乎", True],
        ["？", False, True],
    ]
    assert_tokens_equals(s, classical_chinese, expected)


def test_sample_2(classical_chinese):
    "Sample text parsed, spaces removed."
    s = """學  而時習 之，不亦說乎？
有朋    自遠方來，不亦樂乎？"""

    expected = [
        ["學", True],
        ["而", True],
        ["時", True],
        ["習", True],
        ["之", True],
        ["，", False],
        ["不", True],
        ["亦", True],
        ["說", True],
        ["乎", True],
        ["？", False, True],
        ["¶", False, True],
        ["有", True],
        ["朋", True],
        ["自", True],
        ["遠", True],
        ["方", True],
        ["來", True],
        ["，", False],
        ["不", True],
        ["亦", True],
        ["樂", True],
        ["乎", True],
        ["？", False, True],
    ]
    assert_tokens_equals(s, classical_chinese, expected)
