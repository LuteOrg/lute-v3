"""
Parser registry tests.
"""

import pytest

from lute.parse.registry import get_parser, available_parsers
from lute.parse.space_delimited_parser import SpaceDelimitedParser

def test_get_parser_by_name():
    p = get_parser('spacedel')
    assert isinstance(p, SpaceDelimitedParser)


def test_get_parser_throws_if_not_found():
    with pytest.raises(ValueError):
        p = get_parser('trash')


def test_list_all_parsers():
    d = available_parsers()
    assert d == { 'spacedel': 'Space Delimited' }
