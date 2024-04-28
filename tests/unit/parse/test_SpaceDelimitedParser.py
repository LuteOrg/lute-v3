"""
SpaceDelimitedParser tests.
"""

import sys
import re
import unicodedata
from lute.parse.space_delimited_parser import SpaceDelimitedParser
from lute.parse.base import ParsedToken


def assert_tokens_equals(text, lang, expected):
    """
    Parsing a text using a language should give the expected parsed tokens.

    expected is given as array of:
    [ original_text, is_word, is_end_of_sentence ]
    """
    p = SpaceDelimitedParser()
    actual = p.get_parsed_tokens(text, lang)
    expected = [ParsedToken(*a) for a in expected]
    assert [str(a) for a in actual] == [str(e) for e in expected]


def assert_string_equals(text, lang, expected):
    """
    Parsing a text with a language's settings should yield tokens.

    Similar to assert_tokens_equals, but it stringizes the tokens, e.g.:
    'Hi.\nGoodbye.' => '[Hi].¶[Goodbye].'
    """
    p = SpaceDelimitedParser()
    actual = p.get_parsed_tokens(text, lang)

    def to_string(tokens):
        ret = ""
        for tok in tokens:
            s = tok.token
            if tok.is_word:
                s = "[" + s + "]"
            ret += s
        return ret

    assert to_string(actual) == expected


def test_end_of_sentence_stored_in_parsed_tokens(spanish):
    "ParsedToken is marked as EOS=True at ends of sentences."
    s = "Tengo un gato.\nTengo dos."

    expected = [
        ("Tengo", True, False),
        (" ", False, False),
        ("un", True, False),
        (" ", False, False),
        ("gato", True, False),
        (".", False, True),
        ("¶", False, True),
        ("Tengo", True, False),
        (" ", False, False),
        ("dos", True, False),
        (".", False, True),
    ]

    assert_tokens_equals(s, spanish, expected)


def test_exceptions_are_considered_when_splitting_sentences(english):
    "Languages can have exceptions (like 'Mrs.') that shouldn't split sentences."
    s = "1. Mrs. Jones is here."

    expected = [
        ("1. ", False, True),
        ("Mrs.", True, False),
        (" ", False, False),
        ("Jones", True, False),
        (" ", False, False),
        ("is", True, False),
        (" ", False, False),
        ("here", True, False),
        (".", False, True),
    ]

    assert_tokens_equals(s, english, expected)


def test_single_que(spanish):
    """
    Sanity check: que with accent was getting mishandled.
    """
    text = "Tengo que y qué."
    expected = [
        ("Tengo", True, False),
        (" ", False, False),
        ("que", True, False),
        (" ", False, False),
        ("y", True, False),
        (" ", False, False),
        ("qué", True, False),
        (".", False, True),
    ]
    assert_tokens_equals(text, spanish, expected)


def test_EE_UU_exception_should_be_considered(spanish):
    """
    An exception containing multiple dots should be one single token.
    """
    s = "Estamos en EE.UU. hola."
    spanish.exceptions_split_sentences = "EE.UU."

    expected = [
        ("Estamos", True, False),
        (" ", False, False),
        ("en", True, False),
        (" ", False, False),
        ("EE.UU.", True, False),
        (" ", False, False),
        ("hola", True, False),
        (".", False, True),
    ]

    assert_tokens_equals(s, spanish, expected)


def test_just_EE_UU(spanish):
    """
    A sentence of a single word, where that word is an exception, should be a single token.
    """
    s = "EE.UU."
    spanish.exceptions_split_sentences = "EE.UU."
    expected = [
        ("EE.UU.", True, False),
    ]
    assert_tokens_equals(s, spanish, expected)


def test_quick_checks(english):
    "Fast sanity checks."
    assert_string_equals("test", english, "[test]")
    assert_string_equals("test.", english, "[test].")
    assert_string_equals('"test."', english, '"[test]."')
    assert_string_equals('"test".', english, '"[test]".')
    assert_string_equals("Hi there.", english, "[Hi] [there].")
    assert_string_equals("Hi there.  Goodbye.", english, "[Hi] [there]. [Goodbye].")
    assert_string_equals("Hi.\nGoodbye.", english, "[Hi].¶[Goodbye].")
    assert_string_equals("He123llo.", english, "[He]123[llo].")
    assert_string_equals("1234", english, "1234")
    assert_string_equals("1234.", english, "1234.")
    assert_string_equals("1234.Hello", english, "1234.[Hello]")


def test_zero_width_non_joiner_retained(german):
    """
    Verify zero-width joiner characters are retained in languages that
    include them as word characters.

    Test case from https://en.wikipedia.org/wiki/Zero-width_non-joiner.
    """
    assert_string_equals("Brotzeit", german, "[Brotzeit]")
    assert_string_equals("Brot\u200czeit", german, "[Brot\u200czeit]")


def test_zero_width_joiner_retained(hindi):
    """
    Verify zero-width joiner characters are retained in languages that
    include them as word characters.

    We see them used to replace Hindi conjunct characters with individual consonants.
    """
    assert_string_equals("namaste", hindi, "[namaste]")
    assert_string_equals("नमस्ते", hindi, "[नमस्ते]")
    assert_string_equals("नमस\u200dते", hindi, "[नमस\u200dते]")


def test_default_word_pattern_latin(generic):
    """
    Verify the default word pattern handles Latin alphabets (0000..00FF).
    """

    # Source: https://www.folger.edu/explore/shakespeares-works/henry-v/read/5/2/
    assert_string_equals(
        "Saint Denis be my speed!—donc vôtre est France, et vous êtes mienne.",
        generic,
        " ".join(
            [
                "[Saint]",
                "[Denis]",
                "[be]",
                "[my]",
                "[speed]!—[donc]",
                "[vôtre]",
                "[est]",
                "[France],",
                "[et]",
                "[vous]",
                "[êtes]",
                "[mienne].",
            ]
        ),
    )


def test_default_word_pattern_devanagari(generic):
    """
    Verify the default word pattern handles the Devanagari Unicode block (0900..097F).
    """

    # Source: https://en.wikipedia.org/wiki/Hindi#Sample_text
    assert_string_equals(
        "अनुच्छेद १(एक): सभी मनुष्य जन्म से स्वतन्त्र तथा मर्यादा और अधिकारों में समान होते हैं।",
        generic,
        " ".join(
            [
                "[अनुच्छेद]",
                "१([एक]):",
                "[सभी]",
                "[मनुष्य]",
                "[जन्म]",
                "[से]",
                "[स्वतन्त्र]",
                "[तथा]",
                "[मर्यादा]",
                "[और]",
                "[अधिकारों]",
                "[में]",
                "[समान]",
                "[होते]",
                "[हैं]।",
            ]
        ),
    )


def test_default_word_pattern_georgian(generic):
    """
    Verify the default word pattern handles the Georgian Unicode block (10A0..10FF).
    """

    # Source: https://en.wikipedia.org/wiki/Georgian_language#Examples
    assert_string_equals(
        "ყველა ადამიანი იბადება თავისუფალი და თანასწორი თავისი ღირსებითა და უფლებებით.",
        generic,
        " ".join(
            [
                "[ყველა]",
                "[ადამიანი]",
                "[იბადება]",
                "[თავისუფალი]",
                "[და]",
                "[თანასწორი]",
                "[თავისი]",
                "[ღირსებითა]",
                "[და]",
                "[უფლებებით].",
            ]
        ),
    )


def test_default_word_pattern_gothic(generic):
    """
    Verify the default word pattern handles the Gothic Unicode block (10330..1034F).
    This is an import test case because it tests larger Unicode values.
    """

    # Source: https://en.wikipedia.org/wiki/Gothic_language#Examples
    assert_string_equals(
        "𐌰𐍄𐍄𐌰 𐌿𐌽𐍃𐌰𐍂 𐌸𐌿 𐌹𐌽 𐌷𐌹𐌼𐌹𐌽𐌰𐌼", generic, "[𐌰𐍄𐍄𐌰] [𐌿𐌽𐍃𐌰𐍂] [𐌸𐌿] [𐌹𐌽] [𐌷𐌹𐌼𐌹𐌽𐌰𐌼]"
    )


def test_all_chars_in_categories_match_default_word_chars():
    "Default_word_chars builds a range of characters ... ensure chars in categories are all found."
    categories = set(["Cf", "Ll", "Lm", "Lo", "Lt", "Lu", "Mc", "Mn", "Sk"])

    word_chars = SpaceDelimitedParser.get_default_word_characters()
    pattern = rf"[{word_chars}]"
    regex = re.compile(pattern, flags=re.IGNORECASE)
    for i in range(1, sys.maxunicode):
        c = chr(i)
        if unicodedata.category(c) in categories:
            assert regex.match(c), f"Match for {c}"
