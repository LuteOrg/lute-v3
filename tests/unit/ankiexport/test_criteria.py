"""
Selector tests.
"""

from unittest.mock import Mock
import pytest
from lute.ankiexport.selector import evaluate_selector, validate_selector
from lute.ankiexport.exceptions import AnkiExportConfigurationError


@pytest.fixture(name="term")
def fixture_term():
    "Fake term."
    parent = Mock(text="PARENT")
    parent.term_tags = []

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
def test_selector(selector, expected, term):
    "Check selector vs test term."
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
def test_bad_selector_throws(selector, term):
    "Check selector vs test term."
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
