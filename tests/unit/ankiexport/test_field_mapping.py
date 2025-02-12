"""
Field-to-value tests.
"""

from unittest.mock import Mock
import pytest

from lute.ankiexport.exceptions import AnkiExportConfigurationError
from lute.ankiexport.field_mapping import (
    get_values_and_media_mapping,
    validate_mapping,
    get_fields_and_final_values,
)

# pylint: disable=missing-function-docstring


@pytest.mark.parametrize(
    "mapping,msg",
    [
        ({"a": "{ x }"}, 'Invalid field mapping "x"'),
        ({"a": "{ id }", "b": "{ x }"}, 'Invalid field mapping "x"'),
    ],
)
def test_validate_mapping_throws_if_bad_mapping_string(mapping, msg):
    with pytest.raises(AnkiExportConfigurationError, match=msg):
        validate_mapping(mapping)


@pytest.mark.parametrize(
    "mapping,msg",
    [
        ({"a": "{ id }"}, "ok"),
        ({"a": "{ id }", "b": "{ id }"}, "same value twice ok"),
        ({"a": "{ id }", "b": "{ term }"}, "different fields"),
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
    mapping = {
        "id": "{ id }",
        "term": "{ term }",
        "language": "{ language }",
        "translation": "{ translation }",
    }
    values, media = get_values_and_media_mapping(term, refsrepo, mapping)

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
    mapping = {"tags": "{ tags }"}
    values, media = get_values_and_media_mapping(term, refsrepo, mapping)

    assert set(values["tags"].split(", ")) == {"noun", "verb"}
    assert len(media) == 0


def test_filtered_tag_replacements(term):
    refsrepo = Mock()
    mapping = {"mytags": '{ tags:["noun"] }'}
    values, media = get_values_and_media_mapping(term, refsrepo, mapping)
    assert set(values['tags:["noun"]'].split(", ")) == {"noun"}
    assert len(media) == 0


def test_image_handling(term):
    refsrepo = Mock()
    mapping = {"image": "{ image }"}

    values, media = get_values_and_media_mapping(term, refsrepo, mapping)

    assert media == {"LUTE_TERM_1.jpg": "/userimages/42/image.jpg"}, "one image"
    assert '<img src="LUTE_TERM_1.jpg">' in values["image"]


def test_sentence_handling(term):
    refsrepo = Mock()
    refsrepo.find_references_by_id.return_value = {
        "term": [Mock(sentence="Example sentence.")]
    }
    mapping = {"sentence": "{ sentence }"}

    values, media = get_values_and_media_mapping(term, refsrepo, mapping)

    assert values["sentence"] == "Example sentence."
    assert len(media) == 0


def test_get_fields_and_final_values_smoke_test():
    mapping = {
        "a": "{ id }",
        "b": "{ term }",
    }
    replacements = {"id": 42, "term": "rabbit"}
    actual = get_fields_and_final_values(mapping, replacements)
    assert actual == {"a": "42", "b": "rabbit"}


def test_empty_fields_not_posted():
    mapping = {
        "a": "{ id }",
        "b": "{ term }",
    }
    replacements = {"id": 42, "term": ""}
    actual = get_fields_and_final_values(mapping, replacements)
    assert actual == {"a": "42"}
