"""
Term service tests.
"""

import pytest
from lute.models.repositories import TermRepository
from lute.models.term import TermTag
from lute.db import db
from lute.term.service import Service, TermServiceException, BulkTermUpdateData
from tests.utils import add_terms

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


def xxx_test_add_parent_by_id(app_context, spanish):
    [t, p] = add_terms(spanish, ["t", "p"])
    bud = BulkTermUpdateData(parent_id=p.id)
    _apply_updates(bud)
    expected = {"parents": ["p"], "status": 1, "tags": []}
    assert_stringized(t.id, expected, "parent added")


# add a parent by id
# add parent by text
# add parent by id ignores text
# remove all parents
# leave status
# change status
# ... tag tests
# all terms have to be of the same language
# no updates = nothing happens, ok.


def assert_parents(termid, parray, msg=""):
    newt = TermRepository(db.session).find(termid)
    assert [tp.text for tp in newt.parents] == parray, msg


def test_bulk_parent_update_smoke_test(app_context, spanish):
    "Update parent of term."
    [t, _] = add_terms(spanish, ["t", "p"])
    svc = Service(db.session)
    svc.bulk_set_parent("p", [t.id])
    assert_parents(t.id, ["p"], "P added as parent")


def test_bulk_parent_update_no_terms_ok(app_context, spanish):
    "Update parent of term."
    add_terms(spanish, ["t", "p"])
    svc = Service(db.session)
    svc.bulk_set_parent("p", [])
    # ok.


def test_bulk_parent_update_passing_empty_string_removes_parent(app_context, spanish):
    "Update parent of term."
    [t, _] = add_terms(spanish, ["t", "p"])
    svc = Service(db.session)
    svc.bulk_set_parent("p", [t.id])
    assert_parents(t.id, ["p"], "P added as parent")
    svc.bulk_set_parent("", [t.id])
    assert_parents(t.id, [], "removed")


def test_existing_parent_replaced(app_context, spanish):
    "Update parent of term."
    [t, u, _] = add_terms(spanish, ["t", "u", "p"])
    u.add_parent(t)
    db.session.add(u)
    db.session.commit()
    assert_parents(u.id, ["t"], "initial parents")
    assert_parents(t.id, [], "initial parents")

    svc = Service(db.session)
    svc.bulk_set_parent("p", [t.id, u.id])
    assert_parents(u.id, ["p"], "updated")
    assert_parents(t.id, ["p"], "updated")


def test_bulk_parent_update_parent_must_exist(app_context, spanish):
    "Update parent of term."
    [t, _] = add_terms(spanish, ["t", "p"])
    svc = Service(db.session)
    with pytest.raises(TermServiceException, match="Parent xxx not found"):
        svc.bulk_set_parent("xxx", [t.id])


def test_bulk_parent_update_all_terms_must_be_same_lang(app_context, spanish, english):
    "Update parent of term."
    t, _ = add_terms(spanish, ["t", "p"])
    [e] = add_terms(english, ["e"])
    svc = Service(db.session)
    with pytest.raises(TermServiceException, match="Terms not all the same language"):
        svc.bulk_set_parent("p", [t.id, e.id])


# Bulk tag add/remove


def assert_tags(termid, tarray, msg=""):
    newt = TermRepository(db.session).find(termid)
    assert sorted([tp.text for tp in newt.term_tags]) == sorted(tarray), msg


def test_bulk_tag_add_and_remove_smoke_test(app_context, spanish):
    "Update parent of term."
    [t1, t2] = add_terms(spanish, ["t", "p"])
    t1.add_term_tag(TermTag("hello"))
    svc = Service(db.session)

    svc.bulk_add_tags(["x", "y"], [t1.id, t2.id])
    assert_tags(t1.id, ["hello", "x", "y"], "x, y added to t")
    assert_tags(t1.id, ["hello", "y", "x"], "x, y added to t - assert sort")
    assert_tags(t2.id, ["x", "y"], "x, y added to p")

    svc.bulk_add_tags(["x"], [t1.id, t2.id])
    assert_tags(t1.id, ["hello", "x", "y"], "add twice ok")

    svc.bulk_add_tags(["p", "p"], [t1.id, t2.id])
    assert_tags(t1.id, ["hello", "x", "y", "p"], "p added ok")

    svc.bulk_remove_tags(["x", "y", "p"], [t1.id, t2.id])
    assert_tags(t1.id, ["hello"], "x, y removed from t")
    assert_tags(t2.id, [], "x, y removed from p")

    svc.bulk_remove_tags(["unused"], [t1.id, t2.id])
    assert_tags(t1.id, ["hello"], "same")
    assert_tags(t2.id, [], "same")
