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


def assert_stringized(termid, expected, msg=""):
    "Return a term as a string for fast asserts."
    t = TermRepository(db.session).find(termid)
    actual = {
        "parents": sorted([p.text for p in t.parents]),
        "status": t.status,
        "tags": sorted([tag.text for tag in t.term_tags]),
    }
    assert actual == expected, msg


def test_sanity_smoke_stringize(app_context, spanish):
    "Check only"
    t = add_terms(spanish, ["t"])[0]
    expected = {"parents": [], "status": 1, "tags": []}
    assert_stringized(t.id, expected, "initial")


def _apply_updates(bud):
    "Apply BulkTermUpdateData bud."
    svc = Service(db.session)
    svc.apply_bulk_updates(bud)


def test_bulk_updates_all_terms_must_be_same_lang(app_context, spanish, english):
    "Update parent of term."
    t, p = add_terms(spanish, ["t", "p"])
    [e] = add_terms(english, ["e"])
    bud = BulkTermUpdateData(term_ids=[t.id, e.id], parent_id=p.id)
    svc = Service(db.session)
    with pytest.raises(TermServiceException, match="Terms not all the same language"):
        svc.apply_bulk_updates(bud)


def test_add_parent_by_id(app_context, spanish):
    [t, p] = add_terms(spanish, ["t", "p"])
    bud = BulkTermUpdateData(term_ids=[t.id], parent_id=p.id)
    _apply_updates(bud)
    expected = {"parents": ["p"], "status": 1, "tags": []}
    assert_stringized(t.id, expected, "parent added")


def test_remove_all_parents(app_context, spanish):
    [t, p] = add_terms(spanish, ["t", "p"])
    bud = BulkTermUpdateData(term_ids=[t.id], parent_id=p.id)
    _apply_updates(bud)
    expected = {"parents": ["p"], "status": 1, "tags": []}
    assert_stringized(t.id, expected, "parent added")

    bud = BulkTermUpdateData(term_ids=[t.id], remove_parents=True)
    _apply_updates(bud)
    expected = {"parents": [], "status": 1, "tags": []}
    assert_stringized(t.id, expected, "parent removed")


def test_add_parent_by_text_existing_parent(app_context, spanish):
    [t, p] = add_terms(spanish, ["t", "p"])
    bud = BulkTermUpdateData(term_ids=[t.id], parent_text="p")
    _apply_updates(bud)
    expected = {"parents": ["p"], "status": 1, "tags": []}
    assert_stringized(t.id, expected, "parent added")


def test_add_parent_by_text_new_parent(app_context, spanish):
    [t, p] = add_terms(spanish, ["t", "p"])
    bud = BulkTermUpdateData(term_ids=[t.id], parent_text="newparent")
    _apply_updates(bud)
    expected = {"parents": ["newparent"], "status": 1, "tags": []}
    assert_stringized(t.id, expected, "parent added")


def test_add_parent_text_ignored_if_id_present(app_context, spanish):
    [t, p] = add_terms(spanish, ["t", "p"])
    bud = BulkTermUpdateData(term_ids=[t.id], parent_id=p.id, parent_text="ignored")
    _apply_updates(bud)
    expected = {"parents": ["p"], "status": 1, "tags": []}
    assert_stringized(t.id, expected, "parent added")


def test_set_status(app_context, spanish):
    [t] = add_terms(spanish, ["t"])
    bud = BulkTermUpdateData(term_ids=[t.id], change_status=True, status_value=4)
    _apply_updates(bud)
    expected = {"parents": [], "status": 4, "tags": []}
    assert_stringized(t.id, expected, "status")


def test_set_status_skipped_if_change_status_false(app_context, spanish):
    [t] = add_terms(spanish, ["t"])
    bud = BulkTermUpdateData(term_ids=[t.id], change_status=False, status_value=4)
    _apply_updates(bud)
    expected = {"parents": [], "status": 1, "tags": []}
    assert_stringized(t.id, expected, "status unchanged")


def test_bulk_update_tag_add_and_remove_smoke_test(app_context, spanish):
    "Update parent of term."
    [t, t2] = add_terms(spanish, ["t", "p"])
    t.add_term_tag(TermTag("hello"))
    t.add_term_tag(TermTag("there"))
    db.session.add(t)
    db.session.commit()

    expected = {"parents": [], "status": 1, "tags": ["hello", "there"]}
    assert_stringized(t.id, expected, "initial tags")

    bud = BulkTermUpdateData(
        term_ids=[t.id], add_tags=["hello", "cat"], remove_tags=["there", "dog"]
    )
    _apply_updates(bud)

    expected = {"parents": [], "status": 1, "tags": ["cat", "hello"]}
    assert_stringized(t.id, expected, "tags added,removed")

    tagssql = "select TgText from tags order by TgText"
    expected_tags = ["cat", "hello", "there"]
    assert_sql_result(tagssql, expected_tags, "tag created and added if needed")
