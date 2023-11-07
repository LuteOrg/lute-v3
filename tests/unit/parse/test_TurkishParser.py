"""
TurkishParser tests.
"""

from lute.models.term import Term


def test_downcase(turkish):
    "Turkish has problematic 'i' variants."
    cases = [
        ("CAT", "cat"),  # dummy case
        ("İÇİN", "için"),
        ("IŞIK", "ışık"),
        ("İçin", "için"),
        ("Işık", "ışık"),
    ]

    for text, expected_lcase in cases:
        t = Term(turkish, text)
        assert t.text_lc == expected_lcase, text
