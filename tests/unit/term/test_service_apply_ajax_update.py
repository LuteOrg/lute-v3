"""
Term service apply_ajax_update tests.

Generally smoke tests.
"""

import pytest
from lute.models.repositories import TermRepository
from lute.db import db
from lute.term.service import Service, TermServiceException
from tests.utils import add_terms
from tests.dbasserts import assert_sql_result

# pylint: disable=unbalanced-tuple-unpacking,missing-function-docstring


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
        parents = expected["parents"]
        assert parents == sorted([p.text for p in t.parents]), msg
        should_by_sync = len(parents) == 1
        assert t.sync_status == should_by_sync, f"sync status with parents = {parents}"
    if "status" in expected:
        assert expected["status"] == t.status, msg
    if "tags" in expected:
        assert expected["tags"] == sorted([tag.text for tag in t.term_tags]), msg


def _apply_updates(term_id, update_type, values):
    "Apply updates."
    svc = Service(db.session)
    svc.apply_ajax_update(term_id, update_type, values)


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


def test_term_gets_parent_status_if_parent_status_set(app_context, spanish):
    "Smoke test."
    [t, p] = add_terms(spanish, ["T", "P"])
    t.status = 1
    p.status = 4
    db.session.add(t)
    db.session.add(p)
    db.session.commit()

    _apply_updates(t.id, "parents", ["P"])
    expected = {"status": 4}
    assert_updated(t.id, expected, "gets parent's status")
    assert_updated(p.id, expected, "parent keeps status")


def test_term_keeps_status_if_parent_status_unknown(app_context, spanish):
    "Smoke test."
    [t, p] = add_terms(spanish, ["T", "P"])
    t.status = 1
    p.status = 0
    db.session.add(t)
    db.session.add(p)
    db.session.commit()

    _apply_updates(t.id, "parents", ["P"])
    expected = {"status": 1}
    assert_updated(t.id, expected, "keeps own status")
    expected = {"status": 1}
    assert_updated(p.id, expected, "parent gets child's status!")


def test_bad_term_id_throws(app_context):
    svc = Service(db.session)
    with pytest.raises(TermServiceException, match="No term with id -99"):
        svc.apply_ajax_update(-99, "status", 99)


def test_bad_update_type_throws(app_context, spanish):
    svc = Service(db.session)
    [t] = add_terms(spanish, ["T"])
    with pytest.raises(TermServiceException, match="Bad update type"):
        svc.apply_ajax_update(t.id, "trash", 99)


def test_bad_status_throws(app_context, spanish):
    svc = Service(db.session)
    [t] = add_terms(spanish, ["T"])
    with pytest.raises(TermServiceException, match="Bad status value"):
        svc.apply_ajax_update(t.id, "status", 42)


def test_can_remove_values(app_context, spanish):
    "Smoke test."
    [t, _] = add_terms(spanish, ["T", "P"])
    _apply_updates(t.id, "parents", ["P", "X"])
    _apply_updates(t.id, "term_tags", ["tag1", "tag2"])
    _apply_updates(t.id, "translation", "new_translation")
    expected = {
        "translation": "new_translation",
        "parents": ["P", "X"],
        "tags": ["tag1", "tag2"],
    }
    assert_updated(t.id, expected, "smoke all items")

    _apply_updates(t.id, "parents", [])
    _apply_updates(t.id, "term_tags", [])
    _apply_updates(t.id, "translation", "")
    expected = {
        "translation": None,
        "parents": [],
        "tags": [],
    }
    assert_updated(t.id, expected, "smoke all items updated back to nothing")


def test_parent_created_if_needed(app_context, spanish):
    [t, _] = add_terms(spanish, ["T", "P"])
    sql = "select WoText from words order by WoText"
    assert_sql_result(sql, ["P", "T"], "initial state")
    _apply_updates(t.id, "parents", ["P", "X"])
    assert_sql_result(sql, ["P", "T", "X"], "X created")


def test_correct_parent_found_if_has_zero_width_spaces(app_context, spanish):
    [t, _] = add_terms(spanish, ["T", "P Q"])
    sql = "select WoText from words order by WoText"
    assert_sql_result(sql, ["P/ /Q", "T"], "initial state")

    zws = "\u200B"
    parent = f"P{zws} {zws}Q"
    _apply_updates(t.id, "parents", [parent])
    expected = {"parents": [parent]}
    assert_updated(t.id, expected, "correct zws-included parent found")
    assert_sql_result(sql, ["P/ /Q", "T"], "nothing new created")
