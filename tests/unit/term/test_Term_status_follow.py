"""
Term status following.
"""

import pytest

from lute.models.term import Term as DBTerm
from lute.db import db
from tests.dbasserts import assert_sql_result


@pytest.fixture(name="term_family")
def fixture_term_family(app_context, english):
    """
    Term family.

    A
      B - follows
        b1 - follows
        b2 - no
      C - does not follow
        c1 - follows
        c2 - no
    """

    class family:
        "Family of terms."

        def __init__(self):
            "Set up terms."
            # pylint: disable=invalid-name
            A = DBTerm(english, "A")
            B = DBTerm(english, "B")
            B.add_parent(A)
            B.follow_parent = True
            b1 = DBTerm(english, "b1")
            b1.follow_parent = True
            b2 = DBTerm(english, "b2")

            C = DBTerm(english, "C")
            C.add_parent(A)
            c1 = DBTerm(english, "c1")
            c1.follow_parent = True
            c2 = DBTerm(english, "c2")

            db.session.add(A)
            db.session.add(B)
            db.session.add(b1)
            db.session.add(b2)
            db.session.add(C)
            db.session.add(c1)
            db.session.add(c2)
            db.session.commit()

            self.A = A
            self.B = B
            self.b1 = b1
            self.b2 = b2
            self.C = C
            self.c1 = c1
            self.c2 = c2

    f = family()

    expected_initial_state = """
    A: 1
    B: 1
    b/1: 1
    b/2: 1
    C: 1
    c/1: 1
    c/2: 1
    """
    assert_statuses(expected_initial_state, "initial state")

    return f


def assert_statuses(expected, msg):
    "Check the statuses of terms."
    lines = [
        s.strip().replace(":", ";") for s in expected.split("\n") if s.strip() != ""
    ]
    sql = "select WoText, WoStatus from words order by WoTextLC"
    assert_sql_result(sql, lines, msg)


def test_term_follows_parent_status(term_family, app_context):
    "Changing status should propagate down the tree."
    f = term_family
    f.A.status = 4
    db.session.add(f.A)
    db.session.commit()

    expected = """
    A: 4
    B: 4
    b/1: 4
    b/2: 1
    C: 1
    c/1: 1
    c/2: 1
    """

    assert_statuses(expected, "updated")
