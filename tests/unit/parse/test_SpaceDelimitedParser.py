"""
SpaceDelimitedParser tests.
"""

import pytest

from lute.parse.space_delimited_parser import SpaceDelimitedParser
from lute.parse.base import ParsedToken
from lute.models.language import Language


def assert_tokens_equals(text, lang, expected):
    p = SpaceDelimitedParser()
    actual = p.get_parsed_tokens(text, lang)
    expected = [ParsedToken(*a) for a in expected]
    assert [ str(a) for a in actual ] == [ str(e) for e in expected ]


def test_end_of_sentence_stored_in_parsed_tokens(spanish):
    p = SpaceDelimitedParser()
    s = "Tengo un gato.\nTengo dos."
    actual = p.get_parsed_tokens(s, spanish)

    expected = [
        ('Tengo', True, False),
        (' ', False, False),
        ('un', True, False),
        (' ', False, False),
        ('gato', True, False),
        ('.', False, True),
        ('¶', False, True),
        ('Tengo', True, False),
        (' ', False, False),
        ('dos', True, False),
        ('.', False, True)
    ]

    assert_tokens_equals(s, spanish, expected)


def test_exceptions_are_considered_when_splitting_sentences(english):
    p = SpaceDelimitedParser()
    s = "1. Mrs. Jones is here."
    actual = p.get_parsed_tokens(s, english)

    expected = [
        ('1. ', False, True),
        ('Mrs.', True, False),
        (' ', False, False),
        ('Jones', True, False),
        (' ', False, False),
        ('is', True, False),
        (' ', False, False),
        ('here', True, False),
        ('.', False, True)
    ]

    assert_tokens_equals(s, english, expected)


def test_check_tokens(english):
    p = SpaceDelimitedParser()
    s = "1. Mrs. Jones is here."
    actual = p.get_parsed_tokens(s, english)

    expected = [
        ('1. ', False, True),
        ('Mrs.', True, False),
        (' ', False, False),
        ('Jones', True, False),
        (' ', False, False),
        ('is', True, False),
        (' ', False, False),
        ('here', True, False),
        ('.', False, True)
    ]

    assert_tokens_equals(s, english, expected)


def test_single_que(spanish):
    text = "Tengo que y qué."
    expected = [
        ('Tengo', True, False),
        (' ', False, False),
        ('que', True, False),
        (' ', False, False),
        ('y', True, False),
        (' ', False, False),
        ('qué', True, False),
        ('.', False, True)
    ]
    assert_tokens_equals(text, spanish, expected)


def test_EE_UU_exception_should_be_considered(spanish):
    p = SpaceDelimitedParser()
    s = "Estamos en EE.UU. hola."
    spanish.exceptions_split_sentences = "EE.UU."
    actual = p.get_parsed_tokens(s, spanish)

    expected = [
        ('Estamos', True, False),
        (' ', False, False),
        ('en', True, False),
        (' ', False, False),
        ('EE.UU.', True, False),
        (' ', False, False),
        ('hola', True, False),
        ('.', False, True)
    ]

    assert_tokens_equals(s, spanish, expected)


def test_just_EE_UU(spanish):
    p = SpaceDelimitedParser()
    s = "EE.UU."
    spanish.exceptions_split_sentences = "EE.UU."
    actual = p.get_parsed_tokens(s, spanish)

    expected = [
        ('EE.UU.', True, False),
    ]

    assert_tokens_equals(s, spanish, expected)


def assert_string_equals(text, lang, expected):
    p = SpaceDelimitedParser()
    actual = p.get_parsed_tokens(text, lang)

    def to_string(tokens):
        ret = ''
        for tok in tokens:
            s = tok.token
            if tok.is_word:
                s = '[' + s + ']'
            ret += s
        return ret

    assert to_string(actual) == expected


def test_quick_checks(english):
    assert_string_equals("test", english, "[test]")
    assert_string_equals("test.", english, "[test].")
    assert_string_equals('"test."', english, '"[test]."')
    assert_string_equals('"test".', english, '"[test]".')
    assert_string_equals('Hi there.', english, '[Hi] [there].')
    assert_string_equals('Hi there.  Goodbye.', english, '[Hi] [there].  [Goodbye].')
    assert_string_equals("Hi.\nGoodbye.", english, '[Hi].¶[Goodbye].')
    assert_string_equals('He123llo.', english, '[He]123[llo].')
    assert_string_equals('1234', english, '1234')
    assert_string_equals('1234.', english, '1234.')
    assert_string_equals('1234.Hello', english, '1234.[Hello]')
