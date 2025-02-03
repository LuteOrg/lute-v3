"""
Selector tests.
"""

import pytest
from lute.models.term import Term, TermTag
from lute.db import db
from lute.ankiexport.selector import evaluate_selector


def _make_test_term(spanish):
    """Make term"""
    term = Term(spanish, "HOLA")
    parent = Term(spanish, "PARENT")
    term.add_parent(parent)

    term.add_term_tag(TermTag("masc"))
    term.add_term_tag(TermTag("xxx"))

    db.session.add(term)
    db.session.commit()
    return term


@pytest.mark.parametrize(
    "selector,expected",
    [
        ('language:"Spanish"', True),
    ],
)
def test_selector(selector, expected, empty_db, spanish):
    "Check selector vs test term."
    term = _make_test_term(spanish)
    assert evaluate_selector(selector, term) == expected, selector
