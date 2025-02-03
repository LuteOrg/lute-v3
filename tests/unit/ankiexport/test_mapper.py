"""
Field-to-value tests.
"""

import pytest

from lute.ankiexport.exceptions import AnkiExportConfigurationError
from lute.ankiexport.mapper import mapping_as_array

# pylint: disable=missing-function-docstring


def assert_mapping_equals(mapping, expected):
    "Check results"
    result = mapping_as_array(mapping)
    actual = [f"|{d.fieldname}|=>|{d.value}|" for d in result]
    assert actual == expected, mapping


def test_mapping_as_array_valid():
    mapping = """
    a: {{ somefield }}
    b: {{ anotherfield }}
    """
    expected = [
        "|a|=>|{{ somefield }}|",
        "|b|=>|{{ anotherfield }}|",
    ]
    assert_mapping_equals(mapping, expected)


def test_mapping_value_can_contain_colons_and_other_values():
    mapping = """
    a: {{ somefield }}
    b: {{ anotherfield }}: {{ still more }}
    """
    expected = [
        "|a|=>|{{ somefield }}|",
        "|b|=>|{{ anotherfield }}: {{ still more }}|",
    ]
    assert_mapping_equals(mapping, expected)


def test_mapping_as_array_ignores_comments_and_empty_lines():
    mapping = """
    
    # This is a comment
    a: {{ somefield }}
    
    b: {{ anotherfield }}
    # Another comment
    """
    expected = [
        "|a|=>|{{ somefield }}|",
        "|b|=>|{{ anotherfield }}|",
    ]
    assert_mapping_equals(mapping, expected)


def test_mapping_as_array_raises_error_on_invalid_line():
    mapping = """
    a: {{ somefield }}
    invalid_line_without_colon
    """
    with pytest.raises(
        AnkiExportConfigurationError,
        match='Bad mapping line "invalid_line_without_colon" in mapping',
    ):
        mapping_as_array(mapping)


def test_mapping_as_array_raises_error_on_duplicate_fields():
    mapping = """
    a: {{ somefield }}
    b: {{ anotherfield }}
    a: {{ thirdfield }}
    """
    with pytest.raises(AnkiExportConfigurationError, match="Dup field a in mapping"):
        mapping_as_array(mapping)
