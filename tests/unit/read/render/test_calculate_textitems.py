"""
Tests for getting TextItems.
"""

from lute.models.term import Term
from lute.parse.base import ParsedToken
from lute.read.render.calculate_textitems import get_textitems


def make_tokens(token_data):
    "Make ParsedTokens for the data."
    return [ParsedToken(t, 1) for t in token_data]


def assert_renderable_equals(
    language, token_data, term_data, expected, expected_displayed=None
):
    """
    Run the given scenario:

    Given tokens in language, and terms saved in that language,
    the calculator should render the expected terms,
    only displaying the appropriate parts of each.
    """
    tokens = make_tokens(token_data)
    terms = [Term(language, t) for t in term_data]

    tis = get_textitems(tokens, terms, language)
    res = ""
    for ti in tis:
        res += f"[{ti.text}-{ti.token_count}]"

    zws = chr(0x200B)
    res = res.replace(zws, "")

    assert res == expected

    if expected_displayed is not None:
        res = ""
        for ti in tis:
            res += f"[{ti.display_text}-{ti.token_count}]"

        res = res.replace(zws, "")
        assert res == expected_displayed


def test_simple_render(english):
    "Tokens with no defined terms are rendered as-is."
    data = ["some", " ", "data", " ", "here", "."]
    expected = "[some-1][ -1][data-1][ -1][here-1][.-1]"
    assert_renderable_equals(english, data, [], expected)


def test_non_matching_terms_are_ignored(english):
    "Non-match ignored."
    data = ["some", " ", "data", " ", "here", "."]
    expected = "[some-1][ -1][data-1][ -1][here-1][.-1]"
    assert_renderable_equals(english, data, ["ignoreme"], expected)


def test_partial_matching_terms_are_ignored(english):
    "Partial match is not the same as a match."
    data = ["some", " ", "data", " ", "here", "."]
    expected = "[some-1][ -1][data-1][ -1][here-1][.-1]"
    assert_renderable_equals(english, data, ["data he"], expected)


def test_multiword_items_cover_other_items(english):
    """
    Given a multiword term, some of the other terms are hidden.
    """
    data = ["some", " ", "data", " ", "here", "."]
    words = [
        "data here",
    ]
    expected = "[some-1][ -1][data here-3][.-1]"
    assert_renderable_equals(english, data, words, expected)


def test_case_not_considered_for_matches(english):
    "Case doesnt matter."
    data = ["some", " ", "data", " ", "here", "."]
    expected = "[some-1][ -1][data here-3][.-1]"
    assert_renderable_equals(english, data, ["DATA HERE"], expected)


def test_term_found_in_multiple_places(english):
    "Term can be in a few places."
    data = [
        "some",
        " ",
        "data",
        " ",
        "here",
        " ",
        "more",
        " ",
        "data",
        " ",
        "here",
        ".",
    ]
    expected = "[some-1][ -1][data here-3][ -1][more-1][ -1][data here-3][.-1]"
    assert_renderable_equals(english, data, ["DATA HERE"], expected)


def test_overlapping_multiwords(english):
    """
    Given two overlapping terms, they're both displayed,
    but some of the second is cut off.
    """
    data = ["some", " ", "data", " ", "here", "."]
    words = [
        "some data",
        "data here",
    ]
    expected = "[some data-3][data here-3][.-1]"
    expected_displayed = "[some data-3][ here-3][.-1]"
    assert_renderable_equals(english, data, words, expected, expected_displayed)


def test_multiwords_starting_at_same_location(english):
    """
    Test overlapping matches.
    Given two terms that contain the same chars at the start,
    the longer term overwrites the shorter.
    """
    data = ["A", " ", "B", " ", "C", " ", "D"]
    words = [
        "A B",
        "A B C",
    ]
    expected = "[A B C-5][ -1][D-1]"
    assert_renderable_equals(english, data, words, expected)


def test_crazy_case(english):
    """
    Crazy test case covering the scenario in the class docstring.
    """
    data = [
        "A",
        " ",
        "B",
        " ",
        "C",
        " ",
        "D",
        " ",
        "E",
        " ",
        "F",
        " ",
        "G",
        " ",
        "H",
        " ",
        "I",
    ]
    words = [
        "B C",  # J
        "E F G H I",  # K
        "F G",  # L
        "C D E",  # M
    ]
    expected = "[A-1][ -1][B C-3][C D E-5][E F G H I-9]"
    expected_displayed = "[A-1][ -1][B C-3][ D E-5][ F G H I-9]"
    assert_renderable_equals(english, data, words, expected, expected_displayed)


def test_overlapping_term_ids_two_terms(english):
    """
    Test that overlapping_term_ids are correctly populated
    when two terms start at the same position.
    """
    data = ["A", " ", "B", " ", "C"]
    tokens = make_tokens(data)

    term1 = Term(english, "A B")
    term1.id = 100
    term2 = Term(english, "A B C")
    term2.id = 200

    tis = get_textitems(tokens, [term1, term2], english)

    # Find the textitem that's displayed (should be "A B C", the longer one)
    displayed_ti = [ti for ti in tis if ti.wo_id == 200][0]

    # Should have both term IDs, sorted by length (longest first)
    assert displayed_ti.overlapping_term_ids == [200, 100]
    assert displayed_ti.has_overlapping_terms() is True
    assert displayed_ti.overlapping_term_count == 2


def test_overlapping_term_ids_three_nested(english):
    """
    Test three nested overlapping terms: "a", "a cat", "a cat sat".
    """
    data = ["a", " ", "cat", " ", "sat"]
    tokens = make_tokens(data)

    term1 = Term(english, "a")
    term1.id = 10
    term2 = Term(english, "a cat")
    term2.id = 20
    term3 = Term(english, "a cat sat")
    term3.id = 30

    tis = get_textitems(tokens, [term1, term2, term3], english)

    # Find the displayed term (longest: "a cat sat")
    displayed_ti = [ti for ti in tis if ti.wo_id == 30][0]

    # Should have all three term IDs, sorted by length descending
    assert displayed_ti.overlapping_term_ids == [30, 20, 10]
    assert displayed_ti.has_overlapping_terms() is True
    assert displayed_ti.overlapping_term_count == 3


def test_no_overlapping_terms(english):
    """
    Test that single terms have no overlapping_term_ids.
    """
    data = ["hello", " ", "world"]
    tokens = make_tokens(data)

    term1 = Term(english, "hello")
    term1.id = 100

    tis = get_textitems(tokens, [term1], english)

    hello_ti = [ti for ti in tis if ti.wo_id == 100][0]

    # Single term should have no overlaps
    assert hello_ti.overlapping_term_ids == []
    assert hello_ti.has_overlapping_terms() is False
    assert hello_ti.overlapping_term_count == 0


def test_overlapping_ids_ordering(english):
    """
    Test that overlapping term IDs are correctly ordered by token count.
    """
    data = ["look", " ", "forward", " ", "to"]
    tokens = make_tokens(data)

    term1 = Term(english, "forward")
    term1.id = 50
    term2 = Term(english, "look forward to")
    term2.id = 150

    tis = get_textitems(tokens, [term1, term2], english)

    # Find displayed term (should be "look forward to")
    displayed_ti = [ti for ti in tis if ti.wo_id == 150][0]

    # Longest term should come first in overlapping_term_ids
    assert displayed_ti.overlapping_term_ids[0] == 150
    assert displayed_ti.overlapping_term_ids[1] == 50
