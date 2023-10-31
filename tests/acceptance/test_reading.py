"""
Reading acceptance tests.
"""

import yaml
import requests
from pytest_bdd import given, when, then, scenarios, parsers
from tests.acceptance.lute_test_client import LuteTestClient

scenarios('reading.feature')


@given('a running site')
def given_running_site(luteclient):
    "Sanity check!"
    resp = requests.get(luteclient.home, timeout=5)
    assert resp.status_code == 200, f'{luteclient.home} is up'
    luteclient.visit('/')
    assert luteclient.browser.is_text_present('Lute')

@given('demo languages')
def given_demo_langs_loaded(luteclient):
    "Spot check some things exist."
    for s in [ 'English', 'Spanish' ]:
        assert s in luteclient.language_ids, f'Check map for {s}'

@given(parsers.parse('a {lang} book "{title}" with content:\n{c}'))
def given_book(luteclient, lang, title, c):
    luteclient.make_book(title, c, lang)

@when(parsers.parse('I click "{word}" and edit the form:\n{content}'))
def when_click_word_edit_form(luteclient, word, content):
    "The content is assumed to be yaml."
    updates = yaml.safe_load(content)
    luteclient.click_word_fill_form(word, updates)

@when(parsers.parse('I click "{word}" and press hotkey {hotkey}'))
def when_click_word_edit_form(luteclient, word, hotkey):
    luteclient.click_word(word)
    luteclient.press_hotkey(hotkey)

@then(parsers.parse('the page title is {title}'))
def then_title(luteclient, title):
    assert luteclient.browser.title == title

@then(parsers.parse('the reading pane shows:\n{content}'))
def then_read_content(luteclient, content):
    "Check rendered content."
    displayed = luteclient.displayed_text(LuteTestClient.text_and_status_renderer)
    assert content == displayed
