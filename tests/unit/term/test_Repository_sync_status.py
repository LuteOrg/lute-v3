"""
Term Repository tests, with syncing status to parent.
"""

import pytest
from lute.term.model import Repository
from lute.db import db
from tests.dbasserts import assert_sql_result
from tests.utils import add_terms

# pylint: disable=unbalanced-tuple-unpacking, missing-function-docstring,unused-argument


@pytest.fixture(name="repo")
def fixture_repo(app_context):
    return Repository(db.session)


@pytest.fixture(name="t")
def fixture_term(repo, spanish):
    [dt] = add_terms(spanish, ["T"])
    dt.status = 1
    db.session.add(dt)
    db.session.commit()
    yield repo.load(dt.id)


@pytest.fixture(name="p")
def fixture_parent(repo, spanish):
    [dp] = add_terms(spanish, ["P"])
    dp.status = 4
    db.session.add(dp)
    db.session.commit()
    yield repo.load(dp.id)


def assert_statuses(term, expected, msg):
    repo = Repository(db.session)
    repo.add(term)
    repo.commit()
    sql = "select WoText, WoStatus from words order by WoText"
    assert_sql_result(sql, expected, msg)


def test_save_synced_child_with_set_status_updates_parent_status(t, p):
    t.parents = ["P"]
    t.sync_status = True
    t.status = 3
    assert_statuses(t, ["P; 3", "T; 3"], "both updated")

    t.sync_status = False
    t.status = 1
    assert_statuses(t, ["P; 3", "T; 1"], "P not updated")


def test_save_child_with_no_set_status_inherits_parent_status_if_sync(t, p):
    assert_statuses(t, ["P; 4", "T; 1"], "initial state")
    t.parents = ["P"]
    t.sync_status = True
    assert_statuses(t, ["P; 4", "T; 4"], "initial save")


def test_new_parent_gets_child_status_if_sync(t):
    t.parents = ["NEW"]
    t.sync_status = True
    assert_statuses(t, ["NEW; 1", "T; 1"], "initial save")


def test_child_status_changes_dont_affect_others_if_no_sync(t, p):
    t.status = 3
    assert_statuses(t, ["P; 4", "T; 3"], "no change to other")


def test_remove_parent_breaks_sync(t, p):
    t.parents = ["P"]
    t.sync_status = True
    t.status = 3
    assert_statuses(t, ["P; 3", "T; 3"], "both updated")

    t.parents = []
    t.status = 1
    assert_statuses(t, ["P; 3", "T; 1"], "P not updated, no sync")


def test_cant_sync_multiple_parents(t, p):
    t.parents = ["P", "X"]
    t.sync_status = True
    t.status = 2
    assert_statuses(
        t, ["P; 4", "T; 2", "X; 2"], "P no change, X.status defaults to T's"
    )

    t.status = 3
    assert_statuses(t, ["P; 4", "T; 3", "X; 2"], "X not sync'd, multiple parents")

    t.parents = ["X"]
    assert_statuses(t, ["P; 4", "T; 3", "X; 3"], "X sync'd, single parent")
