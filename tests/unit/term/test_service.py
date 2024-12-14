"""
Term service tests.
"""

import pytest
from lute.models.term import Term as DBTerm
from lute.models.repositories import TermRepository
from lute.db import db
from lute.term.service import Service, TermServiceException
from tests.utils import add_terms

# Bulk parent update


def assert_parents(termid, parray, msg=""):
    newt = TermRepository(db.session).find(termid)
    assert [tp.text for tp in newt.parents] == parray, msg


def test_bulk_parent_update_smoke_test(app_context, spanish):
    "Update parent of term."
    [t, p] = add_terms(spanish, ["t", "p"])
    svc = Service(db.session)
    svc.bulk_set_parent("p", [t.id])
    assert_parents(t.id, ["p"], "P added as parent")


def test_bulk_parent_update_no_terms_ok(app_context, spanish):
    "Update parent of term."
    [t, p] = add_terms(spanish, ["t", "p"])
    svc = Service(db.session)
    svc.bulk_set_parent("p", [])
    # ok.


def test_existing_parent_replaced(app_context, spanish):
    "Update parent of term."
    [t, u, p] = add_terms(spanish, ["t", "u", "p"])
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
    [t, p] = add_terms(spanish, ["t", "p"])
    svc = Service(db.session)
    with pytest.raises(TermServiceException, match="Parent xxx not found"):
        svc.bulk_set_parent("xxx", [t.id])


def test_bulk_parent_update_all_terms_must_be_same_lang(app_context, spanish, english):
    "Update parent of term."
    [t, p] = add_terms(spanish, ["t", "p"])
    [e] = add_terms(english, ["e"])
    svc = Service(db.session)
    with pytest.raises(TermServiceException, match="Terms not all the same language"):
        svc.bulk_set_parent("p", [t.id, e.id])
