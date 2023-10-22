from pytest_bdd import given, when, then, scenario, parsers

from lute.db import db
from lute.models.language import Language
from tests.utils import add_terms, make_text, assert_rendered_text_equals

# The current language being used.
language = None

# The Text object
text = None

@scenario('../features/rendering.feature', 'Smoke test')
def test_smoke_test():
    "Smoke test."
    pass

@given('demo data')
def given_demo_data(app_context):
    "Calling app_context loads the demo data."

@given(parsers.parse('language {langname}'))
def given_lang(langname):
    global language
    lang = db.session.query(Language).filter(Language.name == langname).first()
    assert lang.name == langname, 'sanity check'
    language = lang


@given(parsers.parse('terms:\n{content}'))
def given_terms(content):
    terms = content.split("\n")
    add_terms(language, terms)


@given(parsers.parse('text:\n{content}'))
def when_text(content):
    global text
    text = make_text('test', content, language)
    db.session.add(text)
    db.session.commit()


@then(parsers.parse('rendered should be:\n{content}'))
def then_rendered_should_be(content):
    expected = content.split("\n")
    assert_rendered_text_equals(text, expected)
