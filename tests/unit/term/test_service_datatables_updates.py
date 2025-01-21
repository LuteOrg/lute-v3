"""
Term service apply_datatables_update tests.

Generally smoke tests.
"""

import pytest
from lute.models.repositories import TermRepository
from lute.db import db
from lute.term.service import Service, TermServiceException
from tests.utils import add_terms

# from tests.dbasserts import assert_sql_result

# pylint: disable=unbalanced-tuple-unpacking


def assert_updated(termid, expected, msg=""):
    "Return a term as a string for fast asserts."
    t = TermRepository(db.session).find(termid)
    bad_keys = [
        k
        for k in expected.keys()
        if k not in ["parents", "status", "tags", "translation"]
    ]
    assert len(bad_keys) == 0, "no bad keys " + ", ".join(bad_keys)
    if "translation" in expected:
        assert expected["translation"] == t.translation, msg
    if "parents" in expected:
        assert expected["parents"] == sorted([p.text for p in t.parents]), msg
    if "status" in expected:
        assert expected["status"] == t.status, msg
    if "tags" in expected:
        assert expected["tags"] == sorted([tag.text for tag in t.term_tags]), msg


def _apply_updates(term_id, update_type, values):
    "Apply updates."
    svc = Service(db.session)
    svc.apply_datatables_update(term_id, update_type, values)


def test_smoke_test(app_context, spanish):
    "Smoke test."
    [t, _] = add_terms(spanish, ["T", "P"])
    _apply_updates(t.id, "parents", ["P", "X"])
    _apply_updates(t.id, "status", 4)
    _apply_updates(t.id, "term_tags", ["tag1", "tag2"])
    _apply_updates(t.id, "translation", "new_translation")
    expected = {
        "translation": "new_translation",
        "parents": ["P", "X"],
        "status": 4,
        "tags": ["tag1", "tag2"],
    }
    assert_updated(t.id, expected, "smoke all items")


def test_bad_term_id_throws(app_context):
    svc = Service(db.session)
    with pytest.raises(TermServiceException, match="No term with id -99"):
        svc.apply_datatables_update(-99, "status", 99)


def test_bad_update_type_throws(app_context, spanish):
    svc = Service(db.session)
    [t] = add_terms(spanish, ["T"])
    with pytest.raises(TermServiceException, match="Bad update type"):
        svc.apply_datatables_update(t.id, "trash", 99)


# missing status throws
# empty translation ok
# empty tags ok
# empty parents ok
# new parent created in db if needed
# single parent = sync status
# multi = no sync
# finds right parent if has zws in name
# remove all parents
# add, remove tags

### def test_downcasing(app_context, spanish):
###     "Add parent."
###     [t, p] = add_terms(spanish, ["T", "P"])
###     bud = BulkTermUpdateData(term_ids=[t.id], lowercase_terms=False, parent_id=p.id)
###     _apply_updates(bud)
###     expected = {"text": "T", "parents": ["P"], "status": 1, "tags": []}
###     assert_updated(t.id, expected, "no downcasing")
###
###     bud.lowercase_terms = True
###     _apply_updates(bud)
###     expected = {"text": "t", "parents": ["P"], "status": 1, "tags": []}
###     assert_updated(t.id, expected, "t downcased")
###
###
### def test_add_parent_by_id(app_context, spanish):
###     "Add parent."
###     [t, p] = add_terms(spanish, ["T", "p"])
###     bud = BulkTermUpdateData(term_ids=[t.id], parent_id=p.id)
###     _apply_updates(bud)
###     expected = {"text": "T", "parents": ["p"], "status": 1, "tags": []}
###     assert_updated(t.id, expected, "parent added")
###
###
### def test_remove_all_parents(app_context, spanish):
###     "Checkbox to remove all parents."
###     [t, p] = add_terms(spanish, ["t", "p"])
###     bud = BulkTermUpdateData(term_ids=[t.id], parent_id=p.id)
###     _apply_updates(bud)
###     expected = {"parents": ["p"], "status": 1, "tags": []}
###     assert_updated(t.id, expected, "parent added")
###
###     bud = BulkTermUpdateData(term_ids=[t.id], remove_parents=True)
###     _apply_updates(bud)
###     expected = {"parents": [], "status": 1, "tags": []}
###     assert_updated(t.id, expected, "parent removed")
###
###
### def test_add_parent_by_text_existing_parent(app_context, spanish):
###     "Finds the existing parent by id."
###     [t, _] = add_terms(spanish, ["t", "p"])
###     bud = BulkTermUpdateData(term_ids=[t.id], parent_text="p")
###     _apply_updates(bud)
###     expected = {"parents": ["p"], "status": 1, "tags": []}
###     assert_updated(t.id, expected, "parent added")
###
###
### def test_add_parent_by_text_new_parent(app_context, spanish):
###     "User can create a new parent in the tagify parent field."
###     [t] = add_terms(spanish, ["t"])
###     bud = BulkTermUpdateData(term_ids=[t.id], parent_text="newparent")
###     _apply_updates(bud)
###     expected = {"parents": ["newparent"], "status": 1, "tags": []}
###     assert_updated(t.id, expected, "parent added")
###
###
### def test_set_status(app_context, spanish):
###     "Sanity check."
###     [t] = add_terms(spanish, ["t"])
###     bud = BulkTermUpdateData(term_ids=[t.id], change_status=True, status_value=4)
###     _apply_updates(bud)
###     expected = {"parents": [], "status": 4, "tags": []}
###     assert_updated(t.id, expected, "status")
###
###
### def test_bulk_update_tag_add_and_remove_smoke_test(app_context, spanish):
###     "Update parent of term."
###     [t] = add_terms(spanish, ["t"])
###     t.add_term_tag(TermTag("hello"))
###     t.add_term_tag(TermTag("there"))
###     db.session.add(t)
###     db.session.commit()
###
###     expected = {"parents": [], "status": 1, "tags": ["hello", "there"]}
###     assert_updated(t.id, expected, "initial tags")
###
###     bud = BulkTermUpdateData(
###         term_ids=[t.id], add_tags=["hello", "cat"], remove_tags=["there", "dog"]
###     )
###     _apply_updates(bud)
###
###     expected = {"parents": [], "status": 1, "tags": ["cat", "hello"]}
###     assert_updated(t.id, expected, "tags added,removed")
###
###     tagssql = "select TgText from tags order by TgText"
###     expected_tags = ["cat", "hello", "there"]
###     assert_sql_result(tagssql, expected_tags, "tag created and added if needed")
