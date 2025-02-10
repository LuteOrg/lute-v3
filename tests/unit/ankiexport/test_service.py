"""
Service tests.
"""

from unittest.mock import Mock
import pytest
import json
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

    msg = svc.validate_specs_failure_message()
    assert msg == [f"export_name: {expected_error}"], "failure msg"


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
    term = Mock()
    term.id = 1
    term.text = "test"
    term.language.name = "German"
    term.language.id = 42
    term.get_current_image.return_value = "image.jpg"
    term.parents = []
    term.term_tags = [Mock(text="noun"), Mock(text="verb")]
    term.translation = "example translation"
    return term


def test_smoke_ankiconnect_post_data_for_term(term, export_spec):
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

    refsrepo = Mock()
    refsrepo.find_references_by_id.return_value = {
        "term": [Mock(sentence="Example sentence.")]
    }

    pd = svc.get_ankiconnect_post_data_for_term(term, "http://x:42", refsrepo)
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
                                    "c": "test",
                                    "d": "Example sentence.",
                                },
                                "tags": ["lute", "noun", "verb"],
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


def test_todo_bad_spec_mapping_json():
    a = 2
    assert 1 == a, "TODO"
