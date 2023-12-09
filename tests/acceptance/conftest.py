"""
Acceptance test fixtures and step definitions.

Fixtures used in most or all tests:
_environment_check: ensures site is up
chromebrowser: creates a properly configured browser
luteclient: WIPES THE DB and provides helpful wrappers
"""

import os
import tempfile
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
    parser.addoption("--headless", action="store_true", help="Run the test as headless")


@pytest.fixture(name="_environment_check", scope="session")
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

    url = f"http://localhost:{useport}/"
    try:
        requests.get(url, timeout=10)
    except requests.exceptions.ConnectionError:
        pytest.exit(
            f"Unable to reach {url} ... is it running?  Use inv accept to auto-start it"
        )
        print()


@pytest.fixture(name="chromebrowser", scope="session")
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
        chrome_options.add_argument("--headless")  # Enable headless mode

        # Set the window size and ensure no devtools, or errors happen:
        #
        # selenium.common.exceptions.ElementClickInterceptedException:
        # Message: element click intercepted: Element <button id="submit" ... >
        #   is not clickable at poi...
        #
        # Possibly running headless is opening devtools or using
        # a smaller browser window, which affects the layout and
        # hides some elements.  When run in non-headless, all is fine.

        # https://stackoverflow.com/questions/54023497/
        #   python-selenium-chrome-driver-disable-devtools
        chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

        # https://stackoverflow.com/questions/43541925/
        #   how-can-i-set-the-browser-window-size-when-using-google-chrome-headless
        chrome_options.add_argument("window-size=1920,1080")

    # Initialize the browser with ChromeOptions
    browser = Browser("chrome", options=chrome_options)

    # Set up and clean up the browser
    def fin():
        browser.quit()

    request.addfinalizer(fin)

    return browser


@pytest.fixture(name="luteclient")
def fixture_lute_client(request, chromebrowser):
    """
    Start the lute browser.
    """
    useport = request.config.getoption("--port")
    url = f"http://localhost:{useport}"
    c = LuteTestClient(chromebrowser, url)
    yield c


@pytest.fixture(name="_restore_jp_parser")
def fixture_restore_jp_parser(luteclient):
    "Hack for test: restore a parser using the dev api."
    yield
    luteclient.change_parser_registry_key("disabled_japanese", "japanese")


################################
## STEP DEFS


# Setup


@when(parsers.parse("sleep for {seconds}"))
def _sleep(seconds):
    "Hack helper."
    time.sleep(int(seconds))


@given("a running site")
def given_running_site(luteclient):
    "Sanity check!"
    resp = requests.get(luteclient.home, timeout=5)
    assert resp.status_code == 200, f"{luteclient.home} is up"
    luteclient.visit("/")
    assert luteclient.browser.is_text_present("Lute")


@given('I disable the "japanese" parser')
def disable_japanese_parser(luteclient, _restore_jp_parser):
    luteclient.change_parser_registry_key("japanese", "disabled_japanese")


@given('I enable the "japanese" parser')
def enable_jp_parser(luteclient):
    luteclient.change_parser_registry_key("disabled_japanese", "japanese")


# Browsing


@given(parsers.parse('I visit "{p}"'))
def given_visit(luteclient, p):
    "Go to a page."
    luteclient.visit(p)


@when(parsers.parse('I click the "{linktext}" link'))
def when_click_link_text(luteclient, linktext):
    luteclient.browser.links.find_by_text(linktext).click()


@then(parsers.parse("the page title is {title}"))
def then_title(luteclient, title):
    assert luteclient.browser.title == title


@then(parsers.parse('the page contains "{text}"'))
def then_page_contains(luteclient, text):
    assert text in luteclient.browser.html


# Language


@given("demo languages")
def given_demo_langs_loaded(luteclient):
    "Spot check some things exist."
    for s in ["English", "Spanish"]:
        assert s in luteclient.language_ids, f"Check map for {s}"


@given("the demo stories are loaded")
def given_demo_stories_loaded(luteclient):
    luteclient.load_demo_stories()


@given(parsers.parse("I update the {lang} language:\n{content}"))
def given_update_language(luteclient, lang, content):
    "Content is assumed to be yaml."
    updates = yaml.safe_load(content)
    luteclient.edit_language(lang, updates)


# Books


@given(parsers.parse('a {lang} book "{title}" with content:\n{c}'))
def given_book(luteclient, lang, title, c):
    luteclient.make_book(title, c, lang)


@given(parsers.parse('the book table loads "{title}"'))
def given_book_table_wait(luteclient, title):
    "The book table is loaded via ajax, so there's a delay."
    _sleep(1)  # Hack!
    assert title in luteclient.browser.html


@when(parsers.parse('I set the book table filter to "{filt}"'))
def when_set_book_table_filter(luteclient, filt):
    "Set the filter, wait a sec."
    b = luteclient.browser
    b.find_by_tag("input").fill(filt)
    time.sleep(1)


@then(parsers.parse("the book table contains:\n{content}"))
def check_book_table(luteclient, content):
    "Check the table, e.g. content like 'Hola; Spanish; ; 4 (0%);'"
    time.sleep(1)
    assert content == luteclient.get_book_table_content()


# Terms


@given(parsers.parse("a new {lang} term:\n{content}"))
def given_new_term(luteclient, lang, content):
    "The content is assumed to be yaml."
    updates = yaml.safe_load(content)
    luteclient.make_term(lang, updates)


@given(parsers.parse("import term file:\n{content}"))
def import_term_file(luteclient, content):
    "Import the term file."
    luteclient.visit("/")
    luteclient.browser.find_by_css("#menu_terms").mouse_over()
    luteclient.browser.find_by_id("term_import_index").first.click()
    fd, path = tempfile.mkstemp()
    with os.fdopen(fd, "w") as tmp:
        # do stuff with temp file
        tmp.write(content)
    luteclient.browser.attach_file("text_file", path)
    luteclient.browser.find_by_id("btnSubmit").click()


@then(parsers.parse("the term table contains:\n{content}"))
def check_term_table(luteclient, content):
    "Check the table."
    luteclient.visit("/")
    luteclient.browser.find_by_css("#menu_terms").mouse_over()
    luteclient.browser.find_by_id("term_index").first.click()
    time.sleep(1)
    if content == "-":
        content = "No data available in table"
    assert content == luteclient.get_term_table_content()


# Reading


@then(parsers.parse("the reading pane shows:\n{content}"))
def then_read_content(luteclient, content):
    "Check rendered content."
    displayed = luteclient.displayed_text()
    assert content == displayed


@when(parsers.parse("I change the current text content to:\n{content}"))
def when_change_content(luteclient, content):
    "Change the content."
    assert "Reading" in luteclient.browser.title, "sanity check"
    b = luteclient.browser
    b.find_by_id("editText").click()
    b.find_by_id("text").fill(content)
    b.find_by_id("submit").click()


# Reading, terms


@when(parsers.parse('I click "{word}" and edit the form:\n{content}'))
def when_click_word_edit_form(luteclient, word, content):
    "The content is assumed to be yaml."
    updates = yaml.safe_load(content)
    luteclient.click_word_fill_form(word, updates)


@then(parsers.parse('the reading page term form frame contains "{text}"'))
def then_reading_page_term_form_iframe_contains(luteclient, text):
    "Have to get and read the iframe content, it's not in the main browser page."
    with luteclient.browser.get_iframe("wordframe") as iframe:
        assert text in iframe.html


# Reading, word actions


@when(parsers.parse('I click "{word}"'))
def when_click_word(luteclient, word):
    "Click word."
    luteclient.click_word(word)


@when(parsers.parse("I shift click:\n{words}"))
def shift_click_terms(luteclient, words):
    "Shift-click"
    words = words.split("\n")
    luteclient.shift_click_words(words)


@when(parsers.parse('I click "{word}" and press hotkey "{hotkey}"'))
def when_click_word_press_hotkey(luteclient, word, hotkey):
    "Click word and press hotkey."
    luteclient.click_word(word)
    luteclient.press_hotkey(hotkey)


@when(parsers.parse('I hover over "{word}"'))
def when_hover(luteclient, word):
    "Hover over a term."
    els = luteclient.browser.find_by_text(word)
    assert len(els) == 1, f'have single "{word}"'
    els[0].mouse_over()


@when(parsers.parse('I press hotkey "{hotkey}"'))
def when_press_hotkey(luteclient, hotkey):
    "Click word and press hotkey."
    luteclient.press_hotkey(hotkey)


# Reading, paging


@when(parsers.parse("I click the footer green check"))
def when_click_footer_check(luteclient):
    "Click footer."
    luteclient.browser.find_by_id("footerMarkRestAsKnown").click()
    time.sleep(0.1)  # Leave this, remove and test fails.


@when(parsers.parse("I click the footer next page"))
def when_click_footer_next_page(luteclient):
    "Click footer."
    luteclient.browser.find_by_id("footerNextPage").click()
    time.sleep(0.1)  # Leave this, remove and test fails.
