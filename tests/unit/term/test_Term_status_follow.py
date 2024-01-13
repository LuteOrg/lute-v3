"""
Term status following.
"""

from datetime import datetime
import pytest

from lute.models.term import Term as DBTerm, TermTag
from lute.db import db
from lute.term.model import Term, Repository
from tests.dbasserts import assert_sql_result, assert_record_count_equals
from tests.utils import add_terms, make_text


def test_term_follows_parent_status(app_context, english):
    "Create an existing parent."
    p = DBTerm(english, "parent")
    p.status = 1
    t = DBTerm(english, "child")
    t.status = 1
    t.add_parent(p)
    t.follow_parent = True
    db.session.add(t)
    db.session.commit()

    sql = "select WoTextLC, WoStatus from words order by WoTextLC"
    assert_sql_result(sql, ["child; 1", "parent; 1"], "initial state")

    p.status = 4
    db.session.add(p)
    db.session.commit()
    assert_sql_result(sql, ["child; 4", "parent; 4"], "child changed")
