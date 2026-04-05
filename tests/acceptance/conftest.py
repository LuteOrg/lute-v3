"""
Acceptance test fixtures and step definitions.

Fixtures used in most or all tests:
_environment_check: ensures site is up
chromebrowser: creates a properly configured browser
luteclient: WIPES THE DB and provides helpful wrappers
"""

import os
import re
import tempfile
import time
import yaml
import requests

import pytest
from pytest_bdd import given, when, then, parsers
from playwright.sync_api import sync_playwright
from tests.acceptance.lute_test_client import LuteTestClient


def pytest_addoption(parser):
    """
    Command-line args for pytest runs.
    """
    parser.addoption("--port", action="store", type=int, help="Specify the port number")
    parser.addoption("--headless", action="store_true", help="Run the test as headless")
    parser.addoption("--mobile", action="store_true", help="Run tests tagged @mobile")


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

    # Try connecting a few times.
    success = False
    max_attempts = 5
    curr_attempt = 0
    url = f"http://localhost:{useport}/"

    while curr_attempt < max_attempts and not success:
        curr_attempt += 1
        try:
            requests.get(url, timeout=10)
            success = True
        except requests.exceptions.ConnectionError:
            time.sleep(5)

    if not success:
        msg = f"Unable to reach {url} after {curr_attempt} tries ... "
        msg += "is it running?  Use inv accept to auto-start it."
        pytest.exit(msg)
        print()
    else:
        print(f"Connected successfully after {curr_attempt} tries")


@pytest.fixture(name="chromebrowser", scope="session")
def session_chrome_browser(request, _environment_check):
    """
    Create a chrome browser.
    """
    headless = request.config.getoption("--headless")

    playwright = sync_playwright().start()

    launch_options = {
        "timeout": 4000,
        "headless": headless,
        # Chromium-specific launch args
        "args": ["--disable-blink-features=AutomationControlled"],
    }

    browser = playwright.chromium.launch(**launch_options)

    # Device emulation
    context_kwargs = {"viewport": {"width": 1920, "height": 1080}}

    mobile = request.config.getoption("--mobile")
    if mobile:
        context_kwargs = playwright.devices["iPhone SE"]
        ### user_agent = " ".join(
        ###     [
        ###         "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D)",
        ###         "AppleWebKit/535.19 (KHTML, like Gecko)",
        ###         "Chrome/18.0.1025.166 Mobile Safari/535.19",
        ###     ]
        ### )
        ### context_kwargs.update(
        ###     {
        ###         "user_agent": user_agent,
        ###         "viewport": {"width": 375, "height": 667},  # iPhone SE
        ###         # "device_scale_factor": 2,
        ###         "is_mobile": True,
        ###         "has_touch": True,
        ###     }
        ### )

    context = browser.new_context(**context_kwargs)
    context.set_default_timeout(4000)
    page = context.new_page()

    def fin():
        context.close()
        browser.close()
        playwright.stop()

    request.addfinalizer(fin)

    return page  # This is your "browser" equivalent


@pytest.fixture(name="luteclient")
def fixture_lute_client(request, chromebrowser):
    """
    Start the lute browser.
    """
    useport = request.config.getoption("--port")
    mobile = request.config.getoption("--mobile")
    url = f"http://localhost:{useport}"
    c = LuteTestClient(chromebrowser, url, mobile)
    yield c


@pytest.fixture(name="_restore_jp_parser")
def fixture_restore_jp_parser(luteclient):
    "Hack for test: restore a parser using the dev api."
    yield
    luteclient.change_parser_registry_key("disabled_japanese", "japanese")


################################
## STEP DEFS


@given("terminate the test")
def terminate_test():
    raise RuntimeError("Test terminated intentionally :wave:")


# Setup


@when(parsers.parse("sleep for {seconds}"))
def _sleep(seconds):
    "Hack helper."
    time.sleep(float(seconds))


@given("a running site")
def given_running_site(luteclient):
    "Sanity check!"
    resp = requests.get(luteclient.home, timeout=5)
    assert resp.status_code == 200, f"{luteclient.home} is up"
    luteclient.visit("/")
    luteclient.clear_book_filter()
    assert "Lute" in luteclient.page.content()


@given('I disable the "japanese" parser')
def disable_japanese_parser(luteclient, _restore_jp_parser):
    luteclient.change_parser_registry_key("japanese", "disabled_japanese")


@given('I enable the "japanese" parser')
def enable_jp_parser(luteclient):
    luteclient.change_parser_registry_key("disabled_japanese", "japanese")


@given("all page start dates are set to null")
def set_txstartdate_to_null(luteclient):
    "Hack data."
    luteclient.set_txstartdate_to_null()


# Browsing


@given(parsers.parse('I visit "{p}"'))
def given_visit(luteclient, p):
    "Go to a page."
    luteclient.visit(p)


@when(parsers.parse('I click the "{linktext}" link'))
def when_click_link_text(luteclient, linktext):
    luteclient.page.click(f'text="{linktext}"')


@then(parsers.parse("the page title is {title}"))
def then_title(luteclient, title):
    assert luteclient.page.title() == title


@then(parsers.parse('the page contains "{text}"'))
def then_page_contains(luteclient, text):
    assert text in luteclient.page.content()


# Language


@given("demo languages")
def given_demo_langs_loaded(luteclient):
    "Spot check some things exist."
    for s in ["English", "Spanish"]:
        assert s in luteclient.language_ids, f"Check map for {s}"


@given("the demo stories are loaded")
def given_demo_stories_loaded(luteclient):
    "Load the demo stories."
    luteclient.load_demo_stories()
    _sleep(0.2)  # Hack!
    luteclient.visit("/")
    _sleep(0.2)  # Hack!
    luteclient.clear_book_filter()
    _sleep(0.2)  # Hack!


@given("I clear the book filter")
def given_clear_book_filter(luteclient):
    "clear filter."
    luteclient.visit("/")
    luteclient.clear_book_filter()


@given(parsers.parse("I update the {lang} language:\n{content}"))
def given_update_language(luteclient, lang, content):
    "Content is assumed to be yaml."
    updates = yaml.safe_load(content)
    luteclient.edit_language(lang, updates)


# Books


@given(parsers.parse('a {lang} book "{title}" with content:\n{c}'))
def given_book(luteclient, lang, title, c):
    "Make a book."
    luteclient.make_book(title, c, lang)
    _sleep(0.2)  # Hack!


@given(parsers.parse('a {lang} book "{title}" from file {filename}'))
def given_book_from_file(luteclient, lang, title, filename):
    "Book is made from file in sample_files dir."
    thisdir = os.path.dirname(os.path.realpath(__file__))
    fullpath = os.path.join(thisdir, "sample_files", filename)
    luteclient.make_book_from_file(title, fullpath, lang)
    _sleep(0.2)  # Hack!


@given(parsers.parse("a {lang} book from url {url}"))
def given_book_from_url(luteclient, lang, url):
    "Book is made from url in dev_api."
    luteclient.make_book_from_url(url, lang)
    _sleep(0.2)  # Hack!


@given(parsers.parse('the book table loads "{title}"'))
def given_book_table_wait(luteclient, title):
    "The book table is loaded via ajax, so there's a delay."
    _sleep(0.2)  # Hack!
    assert title in luteclient.page.content()


@when(parsers.parse('I set the book table filter to "{filt}"'))
def when_set_book_table_filter(luteclient, filt):
    "Set the filter, wait a sec."
    luteclient.page.locator("input").first.fill(filt)
    time.sleep(0.2)


@then(parsers.parse("the book table contains:\n{content}"))
def check_book_table(luteclient, content):
    "Check the table, e.g. content like 'Hola; Spanish; ; 4 (0%);'"
    time.sleep(0.2)
    assert content == luteclient.get_book_table_content()


@then(parsers.parse("book pages with start dates are:\n{content}"))
def book_page_start_dates_are(luteclient, content):
    assert content == luteclient.get_book_page_start_dates()


@then(parsers.parse("book pages with read dates are:\n{content}"))
def book_page_read_dates_are(luteclient, content):
    assert content == luteclient.get_book_page_read_dates()


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
    luteclient.page.hover("#menu_terms")
    luteclient.page.click("#term_import_index")
    fd, path = tempfile.mkstemp()
    with os.fdopen(fd, "w") as tmp:
        # do stuff with temp file
        tmp.write(content)
    luteclient.page.set_input_files("#text_file", path)
    luteclient.page.click("#create_terms")
    luteclient.page.click("#update_terms")
    luteclient.page.click("#btnSubmit")


@then(parsers.parse("the term table contains:\n{content}"))
def check_term_table(luteclient, content):
    "Check the table."
    luteclient.visit("/")
    luteclient.page.hover("#menu_terms")
    luteclient.page.click("#term_index")
    time.sleep(0.2)
    if content == "-":
        content = "No data available in table"
    assert content == luteclient.get_term_table_content()


@when("click Export CSV")
def click_export_csv(luteclient):
    "Export the term csv"
    luteclient.page.hover("#term_actions")
    luteclient.page.locator("#term_action_export_csv").click()


@then(parsers.parse("exported CSV file contains:\n{content}"))
def check_exported_file(luteclient, content):
    "Check the exported file, replace all dates with placeholder."
    actual = luteclient.get_temp_file_content("export_terms.csv").strip()
    actual = re.sub(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", "DATE_HERE", actual)
    assert content == actual


# Reading


@then(parsers.parse("the reading pane shows:\n{content}"))
def then_read_content(luteclient, content):
    "Check rendered content."
    c = content.replace("\n", "/")
    timeout = 3  # seconds
    poll_frequency = 0.25
    start_time = time.time()
    displayed = luteclient.displayed_text()
    while time.time() - start_time < timeout:
        if c == displayed:
            break
        time.sleep(poll_frequency)
    else:
        assert c == displayed


@when(parsers.parse("I change the current text content to:\n{content}"))
def when_change_content(luteclient, content):
    "Change the content."
    assert "Reading" in luteclient.page.title(), "sanity check"
    p = luteclient.page
    p.locator("div.hamburger-btn").first.click()
    p.locator("#page-operations-title").click()
    p.locator("#editText").click()
    p.locator("#text").fill(content)
    p.locator("#submit").click()


@when(parsers.parse("I add a page {position} current with content:\n{content}"))
def when_add_page(luteclient, position, content):
    "Add a page."
    assert "Reading" in luteclient.page.title(), "sanity check"
    p = luteclient.page
    p.click("div.hamburger-btn")
    p.click("#page-operations-title")
    assert position in ["before", "after"], "sanity check"
    linkid = (
        "#readmenu_add_page_before"
        if position == "before"
        else "#readmenu_add_page_after"
    )
    p.click(linkid)
    p.fill("#text", content)
    p.click("#submit")
    p.reload()


@when(parsers.parse("I go to the {position} page"))
def when_go_to_page(luteclient, position):
    "Go to page."
    assert "Reading" in luteclient.page.title(), "sanity check"
    assert position in ["previous", "next"], "sanity check"

    linkid = "#navPrev" if position == "previous" else "#navNext"
    luteclient.page.click(linkid)
    time.sleep(0.2)  # Assume this is necessary for ajax reload.
    # Don't reload, as it seems to nullify the nav click.
    # b.reload()


@given(parsers.parse("I peek at page {pagenum}"))
def given_peek_at_page(luteclient, pagenum):
    "Peek at a page of the current book."
    currurl = luteclient.page.url
    peekurl = re.sub(r"/page/.*", f"/peek/{pagenum}", currurl)
    luteclient.visit(peekurl)


@when(parsers.parse("I delete the current page"))
def when_delete_current_page(luteclient):
    "Delete the current page."
    assert "Reading" in luteclient.page.title(), "sanity check"
    luteclient.page.click("div.hamburger-btn")
    luteclient.page.click("#page-operations-title")
    luteclient.page.on("dialog", lambda dialog: dialog.accept())
    luteclient.page.click("#readmenu_delete_page")
    luteclient.page.reload()


# Reading, terms


@when(parsers.parse('I click "{word}" and edit the form:\n{content}'))
def when_click_word_edit_form(luteclient, word, content):
    "The content is assumed to be yaml."
    updates = yaml.safe_load(content)
    luteclient.click_word_fill_form(word, updates)


@when(parsers.parse("I edit the bulk edit form:\n{content}"))
def when_post_bulk_edits_while_reading(luteclient, content):
    "The content is assumed to be yaml."
    updates = yaml.safe_load(content)
    luteclient.fill_reading_bulk_edit_form(updates)


@then(parsers.parse('the reading page term form frame contains "{text}"'))
def then_reading_page_term_form_iframe_contains(luteclient, text):
    "Have to get and read the iframe content, it's not in the main browser page."
    iframe = luteclient.page.frame(name="wordframe")
    assert text in iframe.content()


# Reading, word actions


@when(parsers.parse('I click "{word}"'))
def when_click_word(luteclient, word):
    "Click word."
    luteclient.click_word(word)


@then(parsers.parse('the reading page term form shows term "{text}"'))
def then_reading_page_term_form_iframe_shows_term(luteclient, text):
    "Have to get and read the iframe content, it's not in the main browser page."
    iframe = luteclient.page.frame(name="wordframe")
    time.sleep(0.2)  # Hack, test failing.
    term_field = iframe.locator("#text").first
    zws = "\u200B"
    val = term_field.input_value().replace(zws, "")
    assert val == text, "check field value"


@then("the bulk edit term form is shown")
def then_reading_page_bulk_edit_term_form_is_shown(luteclient):
    "Check content."
    then_reading_page_term_form_iframe_contains(luteclient, "Updating")


@then("the term form is hidden")
def then_reading_page_term_form_is_hidden(luteclient):
    "Set to blankn"
    iframe_element = luteclient.page.locator("#wordframeid").first
    iframe_src = iframe_element.get_attribute("src")
    blanks = ["about:blank", "http://localhost:5001/read/empty", "/read/empty"]
    assert iframe_src in blanks, "Is blank"


@when(parsers.parse("I shift click:\n{words}"))
def shift_click_terms(luteclient, words):
    "Shift-click"
    words = words.split("\n")
    luteclient.shift_click_words(words)


@when(parsers.parse('I shift-drag from "{wstart}" to "{wend}"'))
def shift_drag(luteclient, wstart, wend):
    "shift-drag highlights multiple words, copies to clipboard."
    luteclient.shift_drag(wstart, wend)


@when(parsers.parse('I drag from "{wstart}" to "{wend}"'))
def drag(luteclient, wstart, wend):
    "shift-drag highlights multiple words, copies to clipboard."
    luteclient.drag(wstart, wend)


@when(parsers.parse('I click "{word}" and press hotkey "{hotkey}"'))
def when_click_word_press_hotkey(luteclient, word, hotkey):
    "Click word and press hotkey."
    luteclient.click_word(word)
    luteclient.press_hotkey(hotkey)


@when(parsers.parse('I hover over "{word}"'))
def when_hover(luteclient, word):
    "Hover over a term."
    els = luteclient.page.locator(f"text={word}")
    assert els.count() == 1, f'have single "{word}"'
    els.first.hover()


@when(parsers.parse('I press hotkey "{hotkey}"'))
def when_press_hotkey(luteclient, hotkey):
    "Press hotkey."
    luteclient.press_hotkey(hotkey)


@given(parsers.parse('I set hotkey "{hotkey}" to "{value}"'))
def given_set_hotkey(luteclient, hotkey, value):
    "Set a hotkey to be X."
    luteclient.hack_set_hotkey(hotkey, value)


# Reading, paging


@when(parsers.parse("I click the footer green check"))
def when_click_footer_check(luteclient):
    "Click footer."
    luteclient.page.click("#footerMarkRestAsKnownNextPage")
    time.sleep(0.1)  # Leave this, remove and test fails.


@when(parsers.parse("I click the footer next page"))
def when_click_footer_next_page(luteclient):
    "Click footer."
    luteclient.page.click("#footerNextPage")
    time.sleep(0.1)  # Leave this, remove and test fails.
