import requests

from pytest_bdd import given, when, then, scenarios, parsers

from lute.db import db
from lute.models.language import Language
from lute.models.term import Term
from lute.term.model import Repository
from lute.read.service import get_paragraphs, set_unknowns_to_known, bulk_status_update

from tests.utils import add_terms, make_text
from tests.dbasserts import assert_sql_result
from tests.acceptance.lute_test_client import LuteTestClient


scenarios('reading.feature')


@given('a running site')
def given_running_site(luteclient):
    "Sanity check!"
    resp = requests.get(luteclient.home)
    assert resp.status_code == 200, f'{luteclient.home} is up'
    luteclient.visit('/')
    assert luteclient.browser.is_text_present('Lute')

@given('demo languages')
def given_demo_langs_loaded(luteclient):
    "Spot check some things exist."
    for s in [ 'English', 'Spanish' ]:
        assert s in luteclient.language_ids, f'Check map for {s}'

@when(parsers.parse('I create a {lang} book "{title}" with content:\n{c}'))
def when_book(luteclient, lang, title, c):
    luteclient.make_book(title, c, lang)

@then(parsers.parse('the page title is {title}'))
def then_title(luteclient, title):
    assert luteclient.browser.title == title

@then(parsers.parse('the reading pane shows:\n{content}'))
def then_read_content(luteclient, content):
    displayed = luteclient.displayed_text(LuteTestClient.text_and_status_renderer)
    assert content == displayed
