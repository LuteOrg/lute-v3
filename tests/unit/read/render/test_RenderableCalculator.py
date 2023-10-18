import pytest
from lute.models.term import Term
from lute.models.language import Language
from lute.read.render.renderable_calculator import RenderableCalculator
from lute.read.render.text_token import TextToken


def make_tokens(token_data):
    def make_token(arr):
        t = TextToken()
        t.order = arr[0]
        t.tok_text = arr[1]
        t.is_word = 1
        return t
    return [make_token(t) for t in token_data]


def assert_renderable_equals(english, token_data, word_data, expected, expected_displayed=None):
    tokens = make_tokens(token_data)

    def make_term(arr):
        eng = Language.make_english()
        w = Term(eng, arr[0])
        return w
    words = [make_term(t) for t in word_data]

    rc = RenderableCalculator()
    en = english
    rcs = rc.main(en, words, tokens)
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
                res += f"[{rc.displaytext}-{rc.length}]"

        res = res.replace(zws, '')
        assert res == expected_displayed


def test_simple_render(english):
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
        rcs = rc.main(english, [], tokens)


def test_multiword_items_cover_other_items(english):
    data = [
        [1, 'some'],
        [5, 'here'],
        [4, ' '],
        [3, 'data'],
        [2, ' '],
        [6, '.'],
    ]
    words = [
        ['data here'],
    ]
    expected = '[some-1][ -1][data here-3][.-1]'
    assert_renderable_equals(english, data, words, expected)


def test_overlapping_multiwords(english):
    data = [
        [1, 'some'],
        [2, ' '],
        [3, 'data'],
        [4, ' '],
        [5, 'here'],
        [6, '.'],
    ]
    words = [
        ['some data'],
        ['data here'],
    ]
    expected = '[some data-3][data here-3][.-1]'
    expected_displayed = '[some data-3][ here-3][.-1]'
    assert_renderable_equals(english, data, words, expected, expected_displayed)


def test_multiwords_starting_at_same_location(english):
    chars = list('A B C D')
    data = [[i + 1, c] for i, c in enumerate(chars)]
    words = [
        ['A B'],
        ['A B C'],
    ]
    expected = '[A B C-5][ -1][D-1]'
    assert_renderable_equals(english, data, words, expected)


def test_crazy_case(english):
    chars = list('A B C D E F G H I')
    data = [[i + 1, c] for i, c in enumerate(chars)]
    words = [
        ['B C'],  # J
        ['E F G H I'],  # K
        ['F G'],  # L
        ['C D E'],  # M
    ]
    expected = '[A-1][ -1][B C-3][C D E-5][E F G H I-9]'
    expected_displayed = '[A-1][ -1][B C-3][ D E-5][ F G H I-9]'
    assert_renderable_equals(english, data, words, expected, expected_displayed)
