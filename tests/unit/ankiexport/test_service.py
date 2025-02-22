"""
Service tests.
"""

import json
from unittest.mock import Mock
import pytest
from lute.models.srsexport import SrsExportSpec
from lute.ankiexport.service import Service

# pylint: disable=missing-function-docstring


@pytest.fixture(name="export_spec")
def fixture_spec():
    spec = SrsExportSpec()
    spec.id = 1
    spec.export_name = "export_name"
    spec.criteria = 'language:"German"'
    spec.deck_name = "good_deck"
    spec.note_type = "good_note"
    spec.field_mapping = json.dumps({"a": "{ language }"})
    spec.active = True
    return spec


def test_validate_returns_empty_hash_if_all_ok(export_spec):
    anki_decks = ["good_deck"]
    anki_notes = {"good_note": ["a", "b"]}
    svc = Service(anki_decks, anki_notes, [export_spec])
    result = svc.validate_specs()
    assert len(result) == 0, "No problems"
    msg = svc.validate_specs_failure_message()
    assert len(msg) == 0, "failure msg"


@pytest.mark.parametrize(
    "prop_name,prop_value,expected_error",
    [
        (
            "criteria",
            'lanxxguage:"German"',
            'Criteria syntax error at position 0 or later: lanxxguage:"German"',
        ),
        ("deck_name", "missing_deck", 'No deck name "missing_deck"'),
        ("note_type", "missing_note", 'No note type "missing_note"'),
        (
            "field_mapping",
            json.dumps({"xx": "{ language }"}),
            "Note type good_note does not have field(s): xx",
        ),
        (
            "field_mapping",
            json.dumps({"a": "{ bad_value }"}),
            'Invalid field mapping "bad_value"',
        ),
        (
            "field_mapping",
            "this_is_not_valid_json",
            "Mapping is not valid json",
        ),
    ],
)
def test_validate_spec_returns_array_of_errors(
    prop_name, prop_value, expected_error, export_spec
):
    anki_decks = ["good_deck"]
    anki_notes = {"good_note": ["a", "b"]}
    setattr(export_spec, prop_name, prop_value)
    svc = Service(anki_decks, anki_notes, [export_spec])
    result = svc.validate_spec(export_spec)
    assert result == [expected_error]

    export_spec.active = False
    assert len(svc.validate_spec(export_spec)) == 0, "no errors for inactive spec"


def test_validate_specs_returns_dict_of_export_ids_and_errors(export_spec):
    anki_decks = ["good_deck"]
    anki_notes = {"good_note": ["a", "b"]}
    export_spec.deck_name = "missing_deck"
    svc = Service(anki_decks, anki_notes, [export_spec])
    result = svc.validate_specs()
    assert result == {export_spec.id: 'No deck name "missing_deck"'}

    msg = svc.validate_specs_failure_message()
    assert msg == ['export_name: No deck name "missing_deck"'], "failure msg"


def test_validate_only_checks_active_specs(export_spec):
    anki_decks = ["good_deck"]
    anki_notes = {"good_note": ["a", "b"]}
    export_spec.criteria = "xxx={yyy}"
    svc = Service(anki_decks, anki_notes, [export_spec])
    result = svc.validate_specs()
    assert export_spec.id in result, "should have a problem, sanity check"

    export_spec.active = False
    result = svc.validate_specs()
    assert len(result) == 0, "No problems"
    msg = svc.validate_specs_failure_message()
    assert len(msg) == 0, "failure msg"


@pytest.fixture(name="term")
def fixture_term():
    zws = "\u200B"
    term = Mock()
    term.id = 1
    term.text = f"test{zws} {zws}term"
    term.romanization = "blah-blah"
    term.language.name = "German"
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


def test_smoke_ankiconnect_post_data_for_term(term, export_spec):
    anki_decks = ["good_deck"]
    anki_notes = {"good_note": ["a", "b", "c", "d", "e", "f", "g"]}
    export_spec.field_mapping = json.dumps(
        {
            "a": "{ language }",
            "b": "{ image }",
            "c": "{ term }",
            "d": "{ sentence }",
            "e": "{ pronunciation }",
            "f": '{ tags:["noun"] }',
            "g": '{ parents.tags:["parenttag"] }',
        }
    )
    svc = Service(anki_decks, anki_notes, [export_spec])
    result = svc.validate_specs()
    assert len(result) == 0, "No problems, sanity check"

    sentence_lookup = Mock()
    sentence_lookup.get_sentence_for_term.return_value = "Example sentence."

    pd = svc.get_ankiconnect_post_data_for_term(term, "http://x:42", sentence_lookup)
    assert len(pd) != 0, "Got some post data"

    expected = {
        "export_name": {
            "action": "multi",
            "params": {
                "actions": [
                    {
                        "action": "storeMediaFile",
                        "params": {
                            "filename": "LUTE_TERM_1.jpg",
                            "url": "http://x:42/userimages/42/image.jpg",
                        },
                    },
                    {
                        "action": "addNote",
                        "params": {
                            "note": {
                                "deckName": "good_deck",
                                "modelName": "good_note",
                                "fields": {
                                    "a": "German",
                                    "b": '<img src="LUTE_TERM_1.jpg">',
                                    "c": "test term",
                                    "d": "Example sentence.",
                                    "e": "blah-blah",
                                    "f": "noun",
                                    "g": "parenttag",
                                },
                                "tags": ["lute", "noun", "parenttag", "verb", "xyz"],
                            }
                        },
                    },
                ]
            },
        }
    }

    # print("actual")
    # print(pd)
    # print("expected")
    # print(expected)
    assert pd == expected, "PHEW!"


def test_smoke_ankiconnect_post_data_for_term_without_image(term, export_spec):
    term.get_current_image.return_value = None

    anki_decks = ["good_deck"]
    anki_notes = {"good_note": ["a", "b", "c", "d"]}
    export_spec.field_mapping = json.dumps(
        {
            "a": "{ language }",
            "b": "{ image }",
            "c": "{ term }",
            "d": "{ sentence }",
        }
    )
    svc = Service(anki_decks, anki_notes, [export_spec])
    result = svc.validate_specs()
    assert len(result) == 0, "No problems, sanity check"

    sentence_lookup = Mock()
    sentence_lookup.get_sentence_for_term.return_value = "Example sentence."

    pd = svc.get_ankiconnect_post_data_for_term(term, "http://x:42", sentence_lookup)
    assert len(pd) != 0, "Got some post data"

    expected = {
        "export_name": {
            "action": "multi",
            "params": {
                "actions": [
                    {
                        "action": "addNote",
                        "params": {
                            "note": {
                                "deckName": "good_deck",
                                "modelName": "good_note",
                                "fields": {
                                    "a": "German",
                                    # "b": "", image not posted at all.
                                    "c": "test term",
                                    "d": "Example sentence.",
                                },
                                "tags": ["lute", "noun", "parenttag", "verb", "xyz"],
                            }
                        },
                    },
                ]
            },
        }
    }

    # print("actual")
    # print(pd)
    # print("expected")
    # print(expected)
    assert pd == expected, "PHEW!"
