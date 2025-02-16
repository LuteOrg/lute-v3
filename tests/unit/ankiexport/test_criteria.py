"""
Selector tests.
"""

from unittest.mock import Mock
import pytest
from lute.ankiexport.criteria import evaluate_criteria, validate_criteria
from lute.ankiexport.exceptions import AnkiExportConfigurationError


@pytest.fixture(name="term")
def fixture_term():
    "Fake term."
    parent = Mock(text="PARENT")
    parent.term_tags = [Mock(text="parenttag")]

    term = Mock()
    term.id = 1
    term.text = "HOLA"
    term.status = 3
    term.language.name = "Spanish"
    term.language.id = 42
    term.get_current_image.return_value = "image.jpg"
    term.parents = [parent]
    term.term_tags = [Mock(text="masc"), Mock(text="xxx")]
    term.translation = "example translation"
    return term


@pytest.mark.parametrize(
    "criteria,expected",
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
        ('tags:["parenttag"]', False),
        ('parents.tags:["parenttag"]', True),
        ('all.tags:["parenttag"]', True),
        ('parents.count=1 and tags:["fem", "other"] and status<=3', False),
    ],
)
def test_criteria(criteria, expected, term):
    "Check criteria vs test term."
    assert evaluate_criteria(criteria, term) == expected, criteria


def test_blank_criteria_is_always_true(term):
    assert evaluate_criteria("", term) is True, "blank"
    assert evaluate_criteria(None, term) is True, "None"


@pytest.mark.parametrize(
    "criteria",
    [
        ('lanxguage:"Spanish"'),
        ('language="xxx"'),
        ("parents=1"),
        ('tags="masc"'),
        ('tags["fem", "masc"]'),
        ('parents.count=1 and tags["fem", "other"] and status<=3'),
    ],
)
def test_bad_criteria_throws(criteria, term):
    "Check criteria vs test term."
    with pytest.raises(AnkiExportConfigurationError):
        evaluate_criteria(criteria, term)


@pytest.mark.parametrize(
    "criteria",
    [
        ('lanxguage:"Spanish"'),
        ('language="xxx"'),
        ("parents=1"),
        ('tags="masc"'),
        ('tags["fem", "masc"]'),
        ('parents.count=1 and tags["fem", "other"] and status<=3'),
    ],
)
def test_validate_criteria_throws_if_bad(criteria):
    "Check criteria vs test term."
    with pytest.raises(AnkiExportConfigurationError):
        validate_criteria(criteria)
