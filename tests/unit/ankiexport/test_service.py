"""
Service tests.
"""

import pytest

from lute.models.srsexport import SrsExportSpec
from lute.ankiexport.service import Service

# pylint: disable=missing-function-docstring


@pytest.fixture(name="export_spec")
def fixture_spec():
    spec = SrsExportSpec()
    spec.id = 1
    spec.export_name = "name"
    spec.criteria = 'language:"German"'
    spec.deck_name = "good_deck"
    spec.note_type = "good_note"
    spec.field_mapping = "a: {{ language }}"
    spec.active = True
    return spec


def test_validate_returns_empty_hash_if_all_ok(export_spec):
    anki_decks = ["good_deck"]
    anki_notes = {"good_note": ["a", "b"]}
    svc = Service(anki_decks, anki_notes, [export_spec])
    result = svc.validate_specs()
    assert len(result) == 0, "No problems"


@pytest.mark.parametrize(
    "prop_name,prop_value,expected_error",
    [
        (
            "criteria",
            'lanxxguage:"German"',
            'Syntax error at position 0 or later: lanxxguage:"German"',
        ),
        ("deck_name", "missing_deck", 'No deck name: "missing_deck"'),
        ("note_type", "missing_note", 'No note type: "missing_note"'),
        (
            "field_mapping",
            "xx: {{ language }}",
            "Note type good_note does not have field(s): xx",
        ),
        ("field_mapping", "a: {{ bad_value }}", 'Invalid field mapping "bad_value"'),
    ],
)
def test_validate_returns_dict_of_export_ids_and_errors(
    prop_name, prop_value, expected_error, export_spec
):
    anki_decks = ["good_deck"]
    anki_notes = {"good_note": ["a", "b"]}
    setattr(export_spec, prop_name, prop_value)
    svc = Service(anki_decks, anki_notes, [export_spec])
    result = svc.validate_specs()
    assert export_spec.id in result, "should have a problem"
    assert result[export_spec.id] == expected_error


### def assert_mapping_equals(mapping, expected):
###     "Check results"
###     result = mapping_as_array(mapping)
###     actual = [f"|{d.fieldname}|=>|{d.value}|" for d in result]
###     assert actual == expected, mapping
###
###
### def test_mapping_as_array_valid():
###     mapping = """
###     a: {{ somefield }}
###     b: {{ anotherfield }}
###     """
###     expected = [
###         "|a|=>|{{ somefield }}|",
###         "|b|=>|{{ anotherfield }}|",
###     ]
###     assert_mapping_equals(mapping, expected)
###
###
### def test_mapping_value_can_contain_colons_and_other_values():
###     mapping = """
###     a: {{ somefield }}
###     b: {{ anotherfield }}: {{ still more }}
###     """
###     expected = [
###         "|a|=>|{{ somefield }}|",
###         "|b|=>|{{ anotherfield }}: {{ still more }}|",
###     ]
###     assert_mapping_equals(mapping, expected)
###
###
### def test_mapping_as_array_ignores_comments_and_empty_lines():
###     mapping = """
###
###     # This is a comment
###     a: {{ somefield }}
###
###     b: {{ anotherfield }}
###     # Another comment
###     """
###     expected = [
###         "|a|=>|{{ somefield }}|",
###         "|b|=>|{{ anotherfield }}|",
###     ]
###     assert_mapping_equals(mapping, expected)
###
###
### def test_mapping_as_array_raises_error_on_invalid_line():
###     mapping = """
###     a: {{ somefield }}
###     invalid_line_without_colon
###     """
###     with pytest.raises(
###         AnkiExportConfigurationError,
###         match='Bad mapping line "invalid_line_without_colon" in mapping',
###     ):
###         mapping_as_array(mapping)
###
###
### def test_mapping_as_array_raises_error_on_duplicate_fields():
###     mapping = """
###     a: {{ somefield }}
###     b: {{ anotherfield }}
###     a: {{ thirdfield }}
###     """
###     with pytest.raises(
###         AnkiExportConfigurationError, match="Duplicate field a in mapping"
###     ):
###         mapping_as_array(mapping)
###
###
### @pytest.mark.parametrize(
###     "mapping,msg",
###     [
###         ("a: {{ x }}", 'Invalid mapping value "x"'),
###         ("a: {{ id }}\nb: {{ x }}", 'Invalid mapping value "x"'),
###         ("a: {{ id }}\na: {{ term }}", "Duplicate field a in mapping"),
###     ],
### )
### def test_validate_mapping_throws_if_bad_mapping_string(mapping, msg):
###     with pytest.raises(AnkiExportConfigurationError, match=msg):
###         validate_mapping(mapping)
###
###
### @pytest.mark.parametrize(
###     "mapping,msg",
###     [
###         ("a: {{ id }}", "ok"),
###         ("a: {{ id }}\nb: {{ id }}", "same value twice ok"),
###         ("a: {{ id }}\nb: {{ term }}", "different fields"),
###     ],
### )
### def test_validate_mapping_does_not_throw_if_ok(mapping, msg):
###     validate_mapping(mapping)
###     assert True, msg
###
###
### @pytest.fixture(name="term")
### def fixture_term():
###     term = Mock()
###     term.id = 1
###     term.text = "test"
###     term.language.name = "English"
###     term.language.id = 42
###     term.get_current_image.return_value = "image.jpg"
###     term.parents = []
###     term.term_tags = [Mock(text="noun"), Mock(text="verb")]
###     term.translation = "example translation"
###     return term
###
###
### def test_basic_replacements(term):
###     refsrepo = Mock()
###     mapping_string = """
###         id: {{ id }}
###         term: {{ term }}
###         language: {{ language }}
###         translation: {{ translation }}
###     """
###     values, media = get_values_and_media_mapping(term, refsrepo, mapping_string)
###
###     expected = {
###         "id": 1,
###         "term": "test",
###         "parents": "",
###         "tags": "noun, verb",
###         "language": "English",
###         "translation": "example translation",
###     }
###     assert values == expected, "mappings"
###     assert len(media) == 0
###
###
### def test_tag_replacements(term):
###     refsrepo = Mock()
###     mapping_string = "tags: {{ tags }}"
###
###     values, media = get_values_and_media_mapping(term, refsrepo, mapping_string)
###
###     assert set(values["tags"].split(", ")) == {"noun", "verb"}
###     assert len(media) == 0
###
###
### def test_image_handling(term):
###     refsrepo = Mock()
###     mapping_string = "image: {{ image }}"
###
###     values, media = get_values_and_media_mapping(term, refsrepo, mapping_string)
###
###     assert media == {"LUTE_TERM_1.jpg": "42/image.jpg"}, "one image"
###     assert '<img src="LUTE_TERM_1.jpg">' in values["image"]
###
###
### def test_sentence_handling(term):
###     refsrepo = Mock()
###     refsrepo.find_references_by_id.return_value = {
###         "term": [Mock(sentence="Example sentence.")]
###     }
###     mapping_string = "sentence: {{ sentence }}"
###
###     values, media = get_values_and_media_mapping(term, refsrepo, mapping_string)
###
###     assert values["sentence"] == "Example sentence."
###     assert len(media) == 0
###
###
### def test_get_fields_and_final_values_smoke_test():
###     mapping_string = """
###     a: {{ id }}
###     b: {{ term }}
###     """
###     replacements = {"id": 42, "term": "rabbit"}
###     actual = get_fields_and_final_values(mapping_string, replacements)
###     actual = [str(a) for a in actual]
###     assert actual == ["|a|=>|42|", "|b|=>|rabbit|"]
