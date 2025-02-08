"""
Field-to-value tests.
"""

from unittest.mock import Mock
import pytest

from lute.ankiexport.exceptions import AnkiExportConfigurationError
from lute.ankiexport.field_mapping import (
    mapping_as_array,
    get_values_and_media_mapping,
    validate_mapping,
    get_fields_and_final_values,
)

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
    with pytest.raises(
        AnkiExportConfigurationError, match="Duplicate field a in mapping"
    ):
        mapping_as_array(mapping)


@pytest.mark.parametrize(
    "mapping,msg",
    [
        ("a: {{ x }}", 'Invalid field mapping "x"'),
        ("a: {{ id }}\nb: {{ x }}", 'Invalid field mapping "x"'),
        ("a: {{ id }}\na: {{ term }}", "Duplicate field a in mapping"),
    ],
)
def test_validate_mapping_throws_if_bad_mapping_string(mapping, msg):
    with pytest.raises(AnkiExportConfigurationError, match=msg):
        validate_mapping(mapping)


@pytest.mark.parametrize(
    "mapping,msg",
    [
        ("a: {{ id }}", "ok"),
        ("a: {{ id }}\nb: {{ id }}", "same value twice ok"),
        ("a: {{ id }}\nb: {{ term }}", "different fields"),
    ],
)
def test_validate_mapping_does_not_throw_if_ok(mapping, msg):
    validate_mapping(mapping)
    assert True, msg


@pytest.fixture(name="term")
def fixture_term():
    term = Mock()
    term.id = 1
    term.text = "test"
    term.language.name = "English"
    term.language.id = 42
    term.get_current_image.return_value = "image.jpg"
    term.parents = []
    term.term_tags = [Mock(text="noun"), Mock(text="verb")]
    term.translation = "example translation"
    return term


def test_basic_replacements(term):
    refsrepo = Mock()
    mapping_string = """
        id: {{ id }}
        term: {{ term }}
        language: {{ language }}
        translation: {{ translation }}
    """
    values, media = get_values_and_media_mapping(term, refsrepo, mapping_string)

    expected = {
        "id": 1,
        "term": "test",
        "parents": "",
        "tags": "noun, verb",
        "language": "English",
        "translation": "example translation",
    }
    assert values == expected, "mappings"
    assert len(media) == 0


def test_tag_replacements(term):
    refsrepo = Mock()
    mapping_string = "tags: {{ tags }}"

    values, media = get_values_and_media_mapping(term, refsrepo, mapping_string)

    assert set(values["tags"].split(", ")) == {"noun", "verb"}
    assert len(media) == 0


def test_image_handling(term):
    refsrepo = Mock()
    mapping_string = "image: {{ image }}"

    values, media = get_values_and_media_mapping(term, refsrepo, mapping_string)

    assert media == {"LUTE_TERM_1.jpg": "/userimages/42/image.jpg"}, "one image"
    assert '<img src="LUTE_TERM_1.jpg">' in values["image"]


def test_sentence_handling(term):
    refsrepo = Mock()
    refsrepo.find_references_by_id.return_value = {
        "term": [Mock(sentence="Example sentence.")]
    }
    mapping_string = "sentence: {{ sentence }}"

    values, media = get_values_and_media_mapping(term, refsrepo, mapping_string)

    assert values["sentence"] == "Example sentence."
    assert len(media) == 0


def test_get_fields_and_final_values_smoke_test():
    mapping_string = """
    a: {{ id }}
    b: {{ term }}
    """
    replacements = {"id": 42, "term": "rabbit"}
    actual = get_fields_and_final_values(mapping_string, replacements)
    actual = [str(a) for a in actual]
    assert actual == ["|a|=>|42|", "|b|=>|rabbit|"]
