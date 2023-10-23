"""
JapaneseParser tests.
"""

from lute.parse.mecab_parser import JapaneseParser
from lute.parse.base import ParsedToken


def assert_tokens_equals(text, lang, expected):
    """
    Parsing a text using a language should give the expected parsed tokens.

    expected is given as array of:
    [ original_text, is_word, is_end_of_sentence ]
    """
    p = JapaneseParser()
    actual = p.get_parsed_tokens(text, lang)
    expected = [ParsedToken(*a) for a in expected]
    assert [ str(a) for a in actual ] == [ str(e) for e in expected ]



def test_end_of_sentence_stored_in_parsed_tokens(japanese):
    "ParsedToken is marked as EOS=True at ends of sentences."
    s = "元気.元気?元気!\n元気。元気？元気！"

    expected = [
        ( "元気", True ),
        ( ".", False, True ),
        ( "元気", True ),
        ( "?", False, True ),
        ( "元気", True ),
        ( "!", False, True ),
        ( "¶", False, True ),
        ( "元気", True ),
        ( "。", False, True ),
        ( "元気", True ),
        ( "？", False, True ),
        ( "元気", True ),
        ( "！", False, True ),
        ( "¶", False, True )
    ]
    assert_tokens_equals(s, japanese, expected)


def test_readings():
    """
    Parser returns readings if they add value.
    """
    p = JapaneseParser()

    # Don't bother giving reading for a few cases
    no_reading = [
        'NHK',  # roman
        'ツヨイ',  # only katakana
        'どちら'  # only hiragana
    ]

    for c in no_reading:
        assert p.get_reading(c) is None, c

    zws = '\u200B'
    cases = [
        ('強い', 'ツヨイ'),
        ('二人', 'ニニン'),  # ah well, not perfect :-)
        ('強いか', 'ツヨイカ'),
        (f"強い{zws}か", f"ツヨイ{zws}カ"),  # zero-width-space ignored
    ]

    for c in cases:
        assert p.get_reading(c[0]) == c[1], c[0]
