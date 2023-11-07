"""
TermTag tests.
"""

import pytest

from lute.models.term import TermTag
from lute.db import db
from tests.dbasserts import assert_sql_result


@pytest.fixture(name="_hola_tag")
def fixture_hola_tag(app_context):
    "A dummy tag for tests."
    t = TermTag("Hola", "Hola comment")
    db.session.add(t)
    db.session.commit()


def test_save(_hola_tag, app_context):
    "Save saves!"
    sql = "select TgID, TgText, TgComment from tags"
    expected = ["1; Hola; Hola comment"]
    assert_sql_result(sql, expected)


def test_new_dup_tag_text_fails(_hola_tag, app_context):
    "Smoke test of db integrity."
    t2 = TermTag("Hola", "dup")
    db.session.add(t2)
    with pytest.raises(Exception):
        db.session.commit()


def test_find_by_text(_hola_tag, app_context):
    "Find by text returns match."
    retrieved = TermTag.find_by_text("Hola")
    assert retrieved is not None
    assert retrieved.text == "Hola"


def test_find_by_text_returns_null_if_not_exact_match(_hola_tag, app_context):
    "Find returns null if no match."
    assert TermTag.find_by_text("unknown") is None
    assert TermTag.find_by_text("hola") is None


def test_find_or_create_by_text_returns_new_if_no_match(_hola_tag, app_context):
    "Return new."
    assert TermTag.find_by_text("unknown") is None
    t = TermTag.find_or_create_by_text("unknown")
    assert t.text == "unknown", "new tag created"
