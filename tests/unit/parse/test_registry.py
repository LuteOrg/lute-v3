"""
Parser registry tests.
"""

import pytest

from lute.parse.registry import parsers, get_parser, supported_parsers, is_supported
from lute.parse.space_delimited_parser import SpaceDelimitedParser


def test_get_parser_by_name():
    p = get_parser("spacedel")
    assert isinstance(p, SpaceDelimitedParser)


def test_get_parser_throws_if_not_found():
    with pytest.raises(ValueError):
        get_parser("trash")


def test_list_all_parsers():
    "Sanity check only."
    d = supported_parsers()
    assert isinstance(d, dict), "returns a dict"

    p = d["spacedel"]
    print(p)
    assert p == "Space Delimited", "sanity check"


class DummyParser(SpaceDelimitedParser):
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
    parsers["dummy"] = DummyParser
    yield
    del parsers["dummy"]


def test_unavailable_parser_not_included_in_lists(_load_dummy):
    "An unsupported parser shouldn't be available."
    d = supported_parsers()
    assert "dummy" not in d, "not present"
    assert is_supported("dummy") is False, "no"
    with pytest.raises(ValueError):
        get_parser("dummy")
