"""
TermTag tests.
"""

import pytest

from lute.models.term import TermTag
from lute.db import db
from tests.dbasserts import assert_sql_result


@pytest.fixture(name="hola_tag")
def fixture_hola_tag(spanish, app_context):
    t = TermTag("Hola", "Hola comment")
    db.session.add(t)
    db.session.commit()


def test_save(hola_tag, app_context):
    sql = "select TgID, TgText, TgComment from tags"
    expected = ["1; Hola; Hola comment"]
    assert_sql_result(sql, expected)


def test_new_dup_tag_text_fails(hola_tag, spanish, app_context):
    t2 = TermTag("Hola", "dup")
    db.session.add(t2)
    with pytest.raises(Exception):
        db.session.commit()


def test_find_by_text(hola_tag, app_context):
    retrieved = TermTag.find_by_text("Hola")
    assert retrieved is not None
    assert retrieved.text == "Hola"


def test_find_by_text_returns_null_if_not_exact_match(hola_tag, app_context):
    assert TermTag.find_by_text("unknown") is None
    assert TermTag.find_by_text("hola") is None


def test_find_or_create_by_text_returns_new_if_no_match(hola_tag, app_context):
    assert TermTag.find_by_text("unknown") is None
    t = TermTag.find_or_create_by_text("unknown")
    assert t.text == 'unknown', 'new tag created'
