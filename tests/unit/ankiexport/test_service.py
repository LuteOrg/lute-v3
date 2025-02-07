"""
Service tests.
"""

from unittest.mock import Mock
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


def test_smoke_ankiconnect_post_data_for_term(term, export_spec):
    anki_decks = ["good_deck"]
    anki_notes = {"good_note": ["a", "b"]}
    svc = Service(anki_decks, anki_notes, [export_spec])
    result = svc.validate_specs()
    assert len(result) == 0, "No problems, sanity check"

    pd = svc.get_ankiconnect_post_data_for_term(term)
    assert len(pd) != 0, "Got some post data"

    print(pd)
