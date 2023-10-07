"""
SpaceDelimitedParser tests.
"""

import pytest

from lute.parse.space_delimited_parser import SpaceDelimitedParser
from lute.parse.base import ParsedToken
from lute.models.language import Language


class TestSpaceDelimitedParser:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.spanish = Language.make_spanish()

    def assert_tokens_equals(self, text, lang, expected):
        p = SpaceDelimitedParser()
        actual = p.get_parsed_tokens(text, lang)
        expected = [ParsedToken(*a) for a in expected]
        assert actual == expected

    @pytest.mark.group("parser_eos")
    def test_end_of_sentence_stored_in_parsed_tokens(self):
        p = SpaceDelimitedParser()
        s = "Tengo un gato.\nTengo dos."
        actual = p.get_parsed_tokens(s, self.spanish)

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

        self.assert_tokens_equals(s, self.spanish, expected)

    def test_exceptions_are_considered_when_splitting_sentences(self):
        p = SpaceDelimitedParser()
        s = "1. Mrs. Jones is here."
        e = Language.make_english()
        actual = p.get_parsed_tokens(s, e)

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

        self.assert_tokens_equals(s, e, expected)

    def test_check_tokens(self):
        p = SpaceDelimitedParser()
        s = "1. Mrs. Jones is here."
        e = Language.make_english()
        actual = p.get_parsed_tokens(s, e)

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

        self.assert_tokens_equals(s, e, expected)

    @pytest.mark.group("reloadcurr1")
    def test_single_que(self):
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
        self.assert_tokens_equals(text, Language.make_spanish(), expected)

    @pytest.mark.group("eeuu")
    def test_EE_UU_exception_should_be_considered(self):
        p = SpaceDelimitedParser()
        s = "Estamos en EE.UU. hola."
        sp = Language.make_spanish()
        sp.set_lg_exceptions_split_sentences("EE.UU.")
        actual = p.get_parsed_tokens(s, sp)

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

        self.assert_tokens_equals(s, sp, expected)

    @pytest.mark.group("eeuu")
    def test_just_EE_UU(self):
        p = SpaceDelimitedParser()
        s = "EE.UU."
        sp = Language.make_spanish()
        sp.set_lg_exceptions_split_sentences("EE.UU.")
        actual = p.get_parsed_tokens(s, sp)

        expected = [
            ('EE.UU.', True, False),
        ]

        self.assert_tokens_equals(s, sp, expected)

    def assert_string_equals(self, text, lang, expected):
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

    def test_quick_checks(self):
        e = Language.make_english()
        self.assert_string_equals("test", e, "[test]")
        self.assert_string_equals("test.", e, "[test].")
        self.assert_string_equals('"test."', e, '"[test]."')
        self.assert_string_equals('"test".', e, '"[test]".')
        self.assert_string_equals('Hi there.', e, '[Hi] [there].')
        self.assert_string_equals('Hi there.  Goodbye.', e, '[Hi] [there].  [Goodbye].')
        self.assert_string_equals("Hi.\nGoodbye.", e, '[Hi].¶[Goodbye].')
        self.assert_string_equals('He123llo.', e, '[He]123[llo].')
        self.assert_string_equals('1234', e, '1234')
        self.assert_string_equals('1234.', e, '1234.')
        self.assert_string_equals('1234.Hello', e, '1234.[Hello]')
