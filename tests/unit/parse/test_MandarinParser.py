"""
Testing the MandarinParser
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


def test_sample_1(mandarin):
    "Sample text parsed."
    s = "我爱北京天安门。"

    expected = [["我", True], ["爱", True], ["北京", True], ["天安门", True], ["。", False]]
    assert_tokens_equals(s, mandarin, expected)


def test_sample_2(mandarin):
    "Sample text parsed."
    s = "我爱北京天安门。\n"

    expected = [
        ["我", True],
        ["爱", True],
        ["北京", True],
        ["天安门", True],
        ["。", False],
        ["¶", False, True],
    ]
    assert_tokens_equals(s, mandarin, expected)
