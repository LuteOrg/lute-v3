"""
TurkishParser tests.
"""

from lute.parse.space_delimited_parser import TurkishParser
from lute.models.term import Term
from lute.parse.base import ParsedToken


def test_downcase(turkish):
    cases = [
        ( 'CAT', 'cat' ),
        ( 'İÇİN', 'için' ),
        ( 'IŞIK', 'ışık' ),
        ( 'İçin', 'için' ),
        ( 'Işık', 'ışık' )
    ]

    p = turkish.parser
    for text, expected_lcase in cases:
        t = Term(turkish, text)
        assert t.text_lc == expected_lcase, text
