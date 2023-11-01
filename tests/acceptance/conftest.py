"""
Acceptance test fixtures.
"""

import time
import yaml
import requests

import pytest
from pytest_bdd import given, when, then, parsers
from selenium.webdriver.chrome.options import Options as ChromeOptions
from splinter import Browser
from tests.acceptance.lute_test_client import LuteTestClient


def pytest_addoption(parser):
    """
    Command-line args for pytest runs.
    """
    parser.addoption("--port", action="store", type=int, help="Specify the port number")
    parser.addoption("--headless", action='store_true', help="Run the test as headless")


@pytest.fixture(name='_environment_check', scope='session')
def fixture_env_check(request):
    """
    Sanity check that the site is up, port is set.
    """
    useport = request.config.getoption("--port")
    if useport is None:
        # Need to specify the port, e.g.
        # pytest tests/acceptance --port=1234
        # Acceptance tests run using 'inv accept' sort this out automatically.
        pytest.exit("--port not set")

    url = f'http://localhost:{useport}/'
    try:
        resp = requests.get(url)
    except requests.exceptions.ConnectionError:
        pytest.exit(f"Unable to reach {url} ... is it running?  Use inv accept to auto-start it")
        print()


@pytest.fixture(name='chromebrowser', scope='session')
def session_chrome_browser(request, _environment_check):
    """
    Create a chrome browser.

    For some weird reason, this performs **MUCH**
    better than the default "browser" fixture provided by
    splinter/pytest-splinter:

    "with self.browser.get_iframe('wordframe') as iframe"
      - Without this custom fixture: 5+ seconds!
      - With this fixture: 0.03 seconds

    The times were consistent with various options: headless,
    non, virus scanning on/off, etc.
    """
    chrome_options = ChromeOptions()

    headless = request.config.getoption("--headless")
    if headless:
        chrome_options.add_argument('--headless')  # Enable headless mode

    # Initialize the browser with ChromeOptions
    browser = Browser('chrome', options=chrome_options)

    # Set up and clean up the browser
    def fin():
        browser.quit()
    request.addfinalizer(fin)

    return browser



@pytest.fixture(name='luteclient')
def fixture_lute_client(request, chromebrowser):
    """
    Start the lute browser.
    """
    url = f'http://localhost:{useport}/'
    c = LuteTestClient(chromebrowser, url)
    yield c


def _sleep(seconds):
    "Hack helper."
    time.sleep(seconds)

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

@given('the demo stories are loaded')
def given_demo_stories_loaded(luteclient):
    luteclient.load_demo_stories()

@given(parsers.parse('I update the {lang} language:\n{content}'))
def given_update_language(luteclient, lang, content):
    "Content is assumed to be yaml."
    updates = yaml.safe_load(content)
    print('<' * 30)
    print(updates)
    print('>' * 30)
    luteclient.edit_language(lang, updates)

@given(parsers.parse('a {lang} book "{title}" with content:\n{c}'))
def given_book(luteclient, lang, title, c):
    luteclient.make_book(title, c, lang)

@given(parsers.parse('I visit "{p}"'))
def given_visit(luteclient, p):
    "Go to a page."
    luteclient.visit(p)

@given(parsers.parse('the book table loads "{title}"'))
def given_book_table_wait(luteclient, title):
    "The book table is loaded via ajax, so there's a delay."
    _sleep(0.25)  # Hack!
    assert title in luteclient.browser.html

@when(parsers.parse('I click "{word}" and edit the form:\n{content}'))
def when_click_word_edit_form(luteclient, word, content):
    "The content is assumed to be yaml."
    updates = yaml.safe_load(content)
    luteclient.click_word_fill_form(word, updates)

@when(parsers.parse('I click "{word}" and press hotkey {hotkey}'))
def when_click_word_press_hotkey(luteclient, word, hotkey):
    "Click word and press hotkey."
    luteclient.click_word(word)
    luteclient.press_hotkey(hotkey)

@when(parsers.parse('I click the "{linktext}" link'))
def when_click_link_text(luteclient, linktext):
    luteclient.browser.links.find_by_text(linktext).click()

@when(parsers.parse('I click the footer green check'))
def when_click_footer_check(luteclient):
    luteclient.browser.find_by_id('footerMarkRestAsKnown').click()

@when(parsers.parse('I click the footer next page'))
def when_click_footer_next_page(luteclient):
    luteclient.browser.find_by_id('footerNextPage').click()

@then(parsers.parse('the page title is {title}'))
def then_title(luteclient, title):
    assert luteclient.browser.title == title

@then(parsers.parse('the page contains "{text}"'))
def then_page_contains(luteclient, text):
    assert text in luteclient.browser.html

@then(parsers.parse('the reading page term form frame contains "{text}"'))
def then_reading_page_term_form_iframe_contains(luteclient, text):
    "Have to get and read the iframe content, it's not in the main browser page."
    with luteclient.browser.get_iframe('wordframe') as iframe:
        assert text in iframe.html

@then(parsers.parse('the reading pane shows:\n{content}'))
def then_read_content(luteclient, content):
    "Check rendered content."
    displayed = luteclient.displayed_text(LuteTestClient.text_and_status_renderer)
    assert content == displayed
