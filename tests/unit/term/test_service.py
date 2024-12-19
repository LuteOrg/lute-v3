"""
Term service tests.
"""

import pytest
from lute.models.repositories import TermRepository
from lute.models.term import TermTag
from lute.db import db
from lute.term.service import Service, TermServiceException, BulkTermUpdateData
from tests.utils import add_terms
from tests.dbasserts import assert_sql_result

# Bulk parent update

# pylint: disable=unbalanced-tuple-unpacking


def assert_updated(termid, expected, msg=""):
    "Return a term as a string for fast asserts."
    t = TermRepository(db.session).find(termid)
    bad_keys = [
        k for k in expected.keys() if k not in ["parents", "status", "tags", "text"]
    ]
    assert len(bad_keys) == 0, "no bad keys " + ", ".join(bad_keys)
    if "text" in expected:
        assert expected["text"] == t.text, msg
    if "parents" in expected:
        assert expected["parents"] == sorted([p.text for p in t.parents]), msg
    if "status" in expected:
        assert expected["status"] == t.status, msg
    if "tags" in expected:
        assert expected["tags"] == sorted([tag.text for tag in t.term_tags]), msg


def _apply_updates(bud):
    "Apply BulkTermUpdateData bud."
    svc = Service(db.session)
    svc.apply_bulk_updates(bud)


def test_downcasing(app_context, spanish):
    "Add parent."
    [t, p] = add_terms(spanish, ["T", "P"])
    bud = BulkTermUpdateData(term_ids=[t.id], lowercase_terms=False, parent_id=p.id)
    _apply_updates(bud)
    expected = {"text": "T", "parents": ["P"], "status": 1, "tags": []}
    assert_updated(t.id, expected, "no downcasing")

    bud.lowercase_terms = True
    _apply_updates(bud)
    expected = {"text": "t", "parents": ["P"], "status": 1, "tags": []}
    assert_updated(t.id, expected, "t downcased")


def test_bulk_updates_all_terms_must_be_same_lang(app_context, spanish, english):
    "Update parent of term."
    t, p = add_terms(spanish, ["t", "p"])
    [e] = add_terms(english, ["e"])
    bud = BulkTermUpdateData(term_ids=[t.id, e.id], parent_id=p.id)
    svc = Service(db.session)
    with pytest.raises(TermServiceException, match="Terms not all the same language"):
        svc.apply_bulk_updates(bud)


def test_add_parent_by_id(app_context, spanish):
    "Add parent."
    [t, p] = add_terms(spanish, ["T", "p"])
    bud = BulkTermUpdateData(term_ids=[t.id], parent_id=p.id)
    _apply_updates(bud)
    expected = {"text": "T", "parents": ["p"], "status": 1, "tags": []}
    assert_updated(t.id, expected, "parent added")


def test_remove_all_parents(app_context, spanish):
    "Checkbox to remove all parents."
    [t, p] = add_terms(spanish, ["t", "p"])
    bud = BulkTermUpdateData(term_ids=[t.id], parent_id=p.id)
    _apply_updates(bud)
    expected = {"parents": ["p"], "status": 1, "tags": []}
    assert_updated(t.id, expected, "parent added")

    bud = BulkTermUpdateData(term_ids=[t.id], remove_parents=True)
    _apply_updates(bud)
    expected = {"parents": [], "status": 1, "tags": []}
    assert_updated(t.id, expected, "parent removed")


def test_add_parent_by_text_existing_parent(app_context, spanish):
    "Finds the existing parent by id."
    [t, _] = add_terms(spanish, ["t", "p"])
    bud = BulkTermUpdateData(term_ids=[t.id], parent_text="p")
    _apply_updates(bud)
    expected = {"parents": ["p"], "status": 1, "tags": []}
    assert_updated(t.id, expected, "parent added")


def test_add_parent_by_text_new_parent(app_context, spanish):
    "User can create a new parent in the tagify parent field."
    [t] = add_terms(spanish, ["t"])
    bud = BulkTermUpdateData(term_ids=[t.id], parent_text="newparent")
    _apply_updates(bud)
    expected = {"parents": ["newparent"], "status": 1, "tags": []}
    assert_updated(t.id, expected, "parent added")


def test_add_parent_text_ignored_if_id_present(app_context, spanish):
    "Just in case parent_id and parent_text are both sent."
    [t, p] = add_terms(spanish, ["t", "p"])
    bud = BulkTermUpdateData(term_ids=[t.id], parent_id=p.id, parent_text="ignored")
    _apply_updates(bud)
    expected = {"parents": ["p"], "status": 1, "tags": []}
    assert_updated(t.id, expected, "parent added")


def test_set_status(app_context, spanish):
    "Sanity check."
    [t] = add_terms(spanish, ["t"])
    bud = BulkTermUpdateData(term_ids=[t.id], change_status=True, status_value=4)
    _apply_updates(bud)
    expected = {"parents": [], "status": 4, "tags": []}
    assert_updated(t.id, expected, "status")


def test_set_status_skipped_if_change_status_false(app_context, spanish):
    "Sanity check."
    [t] = add_terms(spanish, ["t"])
    bud = BulkTermUpdateData(term_ids=[t.id], change_status=False, status_value=4)
    _apply_updates(bud)
    expected = {"parents": [], "status": 1, "tags": []}
    assert_updated(t.id, expected, "status unchanged")


def test_bulk_update_tag_add_and_remove_smoke_test(app_context, spanish):
    "Update parent of term."
    [t] = add_terms(spanish, ["t"])
    t.add_term_tag(TermTag("hello"))
    t.add_term_tag(TermTag("there"))
    db.session.add(t)
    db.session.commit()

    expected = {"parents": [], "status": 1, "tags": ["hello", "there"]}
    assert_updated(t.id, expected, "initial tags")

    bud = BulkTermUpdateData(
        term_ids=[t.id], add_tags=["hello", "cat"], remove_tags=["there", "dog"]
    )
    _apply_updates(bud)

    expected = {"parents": [], "status": 1, "tags": ["cat", "hello"]}
    assert_updated(t.id, expected, "tags added,removed")

    tagssql = "select TgText from tags order by TgText"
    expected_tags = ["cat", "hello", "there"]
    assert_sql_result(tagssql, expected_tags, "tag created and added if needed")
