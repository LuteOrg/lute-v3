"""
RenderableCalculator tests.
"""

import pytest
from lute.models.term import Term
from lute.read.render.renderable_calculator import RenderableCalculator
from lute.read.render.text_token import TextToken


def make_tokens(token_data):
    "Make TextTokens for the data."
    def make_token(arr):
        t = TextToken()
        t.order = arr[0]
        t.tok_text = arr[1]
        t.is_word = 1
        return t
    return [make_token(t) for t in token_data]


def assert_renderable_equals(language, token_data, term_data, expected, expected_displayed=None):
    """
    Run the given scenario:

    Given tokens in language, and terms saved in that language,
    the calculator should render the expected terms,
    only displaying the appropriate parts of each.
    """
    tokens = make_tokens(token_data)
    terms = [Term(language, t) for t in term_data]

    rc = RenderableCalculator()
    rcs = rc.main(language, terms, tokens)
    res = ''
    for rc in rcs:
        if rc.render:
            res += f"[{rc.text}-{rc.length}]"

    zws = chr(0x200B)
    res = res.replace(zws, '')

    assert res == expected

    if expected_displayed is not None:
        res = ''
        for rc in rcs:
            if rc.render:
                res += f"[{rc.display_text}-{rc.length}]"

        res = res.replace(zws, '')
        assert res == expected_displayed


def test_simple_render(english):
    "Tokens with no defined terms are rendered as-is."
    data = [
        [1, 'some'],
        [2, ' '],
        [3, 'data'],
        [4, ' '],
        [5, 'here'],
        [6, '.'],
    ]
    expected = '[some-1][ -1][data-1][ -1][here-1][.-1]'
    assert_renderable_equals(english, data, [], expected)


def test_data_out_of_order_still_ok(english):
    """
    Tokens will be sorted during the run.
    """
    data = [
        [1, 'some'],
        [5, 'here'],
        [4, ' '],
        [3, 'data'],
        [2, ' '],
        [6, '.'],
    ]
    expected = '[some-1][ -1][data-1][ -1][here-1][.-1]'
    assert_renderable_equals(english, data, [], expected)


def test_tokens_must_be_contiguous(english):
    """
    If tokens aren't contiguous, the algorithm gets confused.
    """
    data = [
        [1, 'some'],
        [5, 'here'],
        [4, ' '],
        [3, 'data'],
        [2, ' '],
        [7, '.'],
    ]
    tokens = make_tokens(data)

    rc = RenderableCalculator()
    with pytest.raises(Exception):
        rc.main(english, [], tokens)


def test_multiword_items_cover_other_items(english):
    """
    Given a multiword term, some of the other terms are hidden.
    """
    data = [
        [1, 'some'],
        [5, 'here'],
        [4, ' '],
        [3, 'data'],
        [2, ' '],
        [6, '.'],
    ]
    words = [
        'data here',
    ]
    expected = '[some-1][ -1][data here-3][.-1]'
    assert_renderable_equals(english, data, words, expected)


def test_overlapping_multiwords(english):
    """
    Given two overlapping terms, they're both displayed,
    but some of the second is cut off.
    """
    data = [
        [1, 'some'],
        [2, ' '],
        [3, 'data'],
        [4, ' '],
        [5, 'here'],
        [6, '.'],
    ]
    words = [
        'some data',
        'data here',
    ]
    expected = '[some data-3][data here-3][.-1]'
    expected_displayed = '[some data-3][ here-3][.-1]'
    assert_renderable_equals(english, data, words, expected, expected_displayed)


def test_multiwords_starting_at_same_location(english):
    """
    Test overlapping matches.
    Given two terms that contain the same chars at the start,
    the longer term overwrites the shorter.
    """
    chars = list('A B C D')
    data = [[i + 1, c] for i, c in enumerate(chars)]
    words = [
        'A B',
        'A B C',
    ]
    expected = '[A B C-5][ -1][D-1]'
    assert_renderable_equals(english, data, words, expected)


def test_crazy_case(english):
    """
    Crazy test case covering the scenario in the class docstring.
    """
    chars = list('A B C D E F G H I')
    data = [[i + 1, c] for i, c in enumerate(chars)]
    words = [
        'B C',  # J
        'E F G H I',  # K
        'F G',  # L
        'C D E',  # M
    ]
    expected = '[A-1][ -1][B C-3][C D E-5][E F G H I-9]'
    expected_displayed = '[A-1][ -1][B C-3][ D E-5][ F G H I-9]'
    assert_renderable_equals(english, data, words, expected, expected_displayed)


# TODO turkish: add turkish check
# TODO japanese: add turkish check
# TODO other languages: add other lang/parser checks
