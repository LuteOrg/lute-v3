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
    SentenceLookup,
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
    zws = "\u200B"
    term = Mock()
    term.id = 1
    term.text = f"test{zws} {zws}term"
    term.romanization = "blah-blah"
    term.language.name = "English"
    term.language.id = 42
    term.get_current_image.return_value = "image.jpg"
    term.term_tags = [Mock(text="noun"), Mock(text="verb")]
    term.translation = f"example{zws} {zws}translation"

    parent = Mock()
    parent.text = "parent-text"
    parent.translation = "parent-transl"
    parent.get_current_image.return_value = None
    parent.term_tags = [Mock(text="parenttag"), Mock(text="xyz")]
    term.parents = [parent]

    return term


def test_basic_replacements(term):
    sentence_lookup = Mock()
    mapping = {
        "id": "{ id }",
        "term": "{ term }",
        "language": "{ language }",
        "translation": "{ translation }",
        "pron": "{ pronunciation }",
    }
    values, media = get_values_and_media_mapping(term, sentence_lookup, mapping)

    expected = {
        "id": 1,
        "term": "test term",
        "parents": "parent-text",
        "tags": "noun, verb",
        "language": "English",
        "translation": "example translation<br>parent-transl",
        "pronunciation": "blah-blah",
    }
    assert values == expected, "mappings"
    assert len(media) == 0


def test_tag_replacements(term):
    sentence_lookup = Mock()
    mapping = {"tags": "{ tags }"}
    values, media = get_values_and_media_mapping(term, sentence_lookup, mapping)

    assert set(values["tags"].split(", ")) == {"noun", "verb"}
    assert len(media) == 0


def test_filtered_tag_replacements(term):
    sentence_lookup = Mock()
    mapping = {"mytags": '{ tags:["noun"] }'}
    values, media = get_values_and_media_mapping(term, sentence_lookup, mapping)
    assert set(values['tags:["noun"]'].split(", ")) == {"noun"}
    assert len(media) == 0


def test_filtered_parents_tag_replacements(term):
    sentence_lookup = Mock()
    mapping = {"mytags": '{ parents.tags:["parenttag"] }'}
    values, media = get_values_and_media_mapping(term, sentence_lookup, mapping)
    assert set(values['parents.tags:["parenttag"]'].split(", ")) == {"parenttag"}
    assert len(media) == 0


def test_image_handling(term):
    sentence_lookup = Mock()
    mapping = {"image": "{ image }"}

    values, media = get_values_and_media_mapping(term, sentence_lookup, mapping)

    assert media == {"LUTE_TERM_1.jpg": "/userimages/42/image.jpg"}, "one image"
    assert '<img src="LUTE_TERM_1.jpg">' in values["image"]


def test_sentence_handling(term):
    zws = "\u200B"
    sentence_lookup = Mock()
    sentence_lookup.get_sentence_for_term.return_value = f"Example{zws} {zws}sentence."
    mapping = {"sentence": "{ sentence }"}

    values, media = get_values_and_media_mapping(term, sentence_lookup, mapping)

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


def test_sentence_lookup_finds_sentence_in_supplied_dict_or_does_db_call():
    refsrepo = Mock()
    refsrepo.find_references_by_id.return_value = {"term": [Mock(sentence="Db lookup")]}
    fixed_sentences = {"42": "Hello"}
    lookup = SentenceLookup(fixed_sentences, refsrepo)
    assert lookup.get_sentence_for_term("42") == "Hello", "looks up"
    assert lookup.get_sentence_for_term(42) == "Hello", "int ok, still finds"
    assert lookup.get_sentence_for_term(99) == "Db lookup", "falls back to db lookup"
    assert lookup.get_sentence_for_term("99") == "Db lookup", "falls back to db lookup"
