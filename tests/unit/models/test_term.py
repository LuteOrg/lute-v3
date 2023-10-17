"""
Term tests.
"""

import pytest
from lute.models.term import Term


def test_cruft_stripped_on_set_word(spanish):
    cases = [
        ('hola', 'hola', 'hola'),
        ('    hola    ', 'hola', 'hola'),
        # This case should never occur:
        # tabs are stripped out of text, and returns mark different sentences.
        # ('   hola\tGATO\nok', 'hola GATO ok', 'hola gato ok'),
    ]

    for text, expected_text, expected_text_lc in cases:
        term = Term(spanish, text)
        assert term.text == expected_text
        assert term.text_lc == expected_text_lc


def test_token_count(english):
    cases = [
        ("hola", 1),
        ("    hola    ", 1),
        ("  hola  gato", 3),
        ("HOLA hay\tgato  ", 5),
        ("  the CAT's pyjamas  ", 7),
        # This only has 9 tokens, because the "'" is included with
        # the following space ("' ").
        ("A big CHUNK O' stuff", 9),
        ("YOU'RE", 3),
        ("...", 1),  # should never happen :-)
    ]

    for text, expected_token_count in cases:
        term = Term(english, text)
        assert term.token_count == expected_token_count



def test_term_left_as_is_if_its_an_exception(spanish):
    spanish.exceptions_split_sentences = 'EE.UU.'

    term = Term(spanish, 'EE.UU.')
    assert term.token_count == 1
    assert term.text == 'EE.UU.'

    term = Term(spanish, 'ee.uu.')
    assert term.token_count == 1
    assert term.text == 'ee.uu.'


def test_cannot_add_self_as_own_parent(spanish):
    t = Term(spanish, 'gato')
    t.add_parent(t)
    assert len(t.parents) == 0

    otherterm = Term(spanish, 'gato')
    t.add_parent(otherterm)
    assert len(t.parents) == 0, 'different object still not added'


# TODO term tests: add/remove image
# TODO term tests: add/remove tags
# TODO term tests: add/remove parents
