"""
Selector tests.
"""

import pytest
from lute.models.term import Term, TermTag
from lute.db import db
from lute.ankiexport.selector import evaluate_selector, validate_selector
from lute.ankiexport.exceptions import AnkiExportConfigurationError


def _make_test_term(spanish):
    """Make term"""
    term = Term(spanish, "HOLA")
    parent = Term(spanish, "PARENT")
    term.add_parent(parent)

    term.add_term_tag(TermTag("masc"))
    term.add_term_tag(TermTag("xxx"))
    term.status = 3

    db.session.add(term)
    db.session.commit()
    return term


@pytest.mark.parametrize(
    "selector,expected",
    [
        ('language:"Spanish"', True),
        ('language:"xxx"', False),
        ("parents.count=1", True),
        ("parents.count==1", True),
        ("parents.count>=0", True),
        ("parents.count>1", False),
        ('tags:"masc"', True),
        ('tags:"fem"', False),
        ('tags:["fem", "masc"]', True),
        ("status<=3", True),
        ("status==1", False),
        ('tags:["fem", "other"]', False),
        ('parents.count=1 and tags:["fem", "other"] and status<=3', False),
    ],
)
def test_selector(selector, expected, empty_db, spanish):
    "Check selector vs test term."
    term = _make_test_term(spanish)
    assert evaluate_selector(selector, term) == expected, selector


@pytest.mark.parametrize(
    "selector",
    [
        ('lanxguage:"Spanish"'),
        ('language="xxx"'),
        ("parents=1"),
        ('tags="masc"'),
        ('tags["fem", "masc"]'),
        ('parents.count=1 and tags["fem", "other"] and status<=3'),
    ],
)
def test_bad_selector_throws(selector, empty_db, spanish):
    "Check selector vs test term."
    term = _make_test_term(spanish)
    with pytest.raises(AnkiExportConfigurationError):
        evaluate_selector(selector, term)


@pytest.mark.parametrize(
    "selector",
    [
        ('lanxguage:"Spanish"'),
        ('language="xxx"'),
        ("parents=1"),
        ('tags="masc"'),
        ('tags["fem", "masc"]'),
        ('parents.count=1 and tags["fem", "other"] and status<=3'),
    ],
)
def test_validate_selector_throws_if_bad(selector):
    "Check selector vs test term."
    with pytest.raises(AnkiExportConfigurationError):
        validate_selector(selector)
