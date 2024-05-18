"""
Parser registry tests.
"""

import pytest

from lute.parse.registry import (
    __LUTE_PARSERS__,
    get_parser,
    supported_parsers,
    is_supported,
)
from lute.parse.space_delimited_parser import SpaceDelimitedParser


def test_get_parser_by_name():
    p = get_parser("spacedel")
    assert isinstance(p, SpaceDelimitedParser)


def test_get_parser_throws_if_not_found():
    with pytest.raises(ValueError):
        get_parser("trash")


def test_supported_parsers():
    "Sanity check only."
    d = supported_parsers()
    assert isinstance(d, list), "returns a list"

    p = [n for n in d if n[0] == "spacedel"][0]
    assert p == ("spacedel", "Space Delimited"), "sanity check"


class DummyParser:
    "Dummy unsupported parser."

    @classmethod
    def is_supported(cls):
        return False

    @classmethod
    def name(cls):
        return "DUMMY"


@pytest.fixture(name="_load_dummy")
def fixture_load_dummy():
    "Add the dummy parser for the test."
    __LUTE_PARSERS__["dummy"] = DummyParser
    yield
    del __LUTE_PARSERS__["dummy"]


def test_unavailable_parser_not_included_in_lists(_load_dummy):
    "An unsupported parser shouldn't be available."
    d = supported_parsers()
    assert "dummy" not in d, "not present"
    assert is_supported("dummy") is False, "no"
    with pytest.raises(ValueError):
        get_parser("dummy")
