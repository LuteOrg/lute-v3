"""
Smoke tests.
"""

import requests
import time
from selenium.webdriver.common.keys import Keys
import pytest


class LuteBrowser:
    """
    Convenience wrapper around the browser.

    Adds the base url to visited urls,
    provides common functions like make_book.

    Also calls the dev_api to set state, etc.
    """
    def __init__(self, b, base_url):
        self.browser = b
        self.base_url = base_url
        self.visit('dev_api/wipe_db')
        self.visit('dev_api/load_demo_languages')

        response = requests.get(f'{base_url}/dev_api/language_ids', timeout=5)
        self.language_ids = response.json()

        self.start = time.perf_counter()
        self.last_step = self.start

    def elapsed(self, step):
        """
        Helper method for sorting out slowness.

        For the step, gives elapsed time since start of
        the LuteBrowser, and since the last recorded step.

        To see this data, have to run the acc. tests with '-s', eg:

        pytest tests/acceptance/test_smoke.py --port=5000 -s
        """
        now = time.perf_counter()
        since_start = now - self.start
        print(step)
        print(f'total elapsed: {since_start}')
        print(f'since last:    {now - self.last_step}')
        self.last_step = now

    def visit(self, suburl):
        "Visit a sub url under the base."
        url = f'{self.base_url}/{suburl}'
        self.browser.visit(url)

    def index(self):
        "Go to home page."
        self.browser.visit('')

    def make_book(self, title, text, langname):
        "Create a book with title, text, and languagename."
        self.visit('book/new')
        self.browser.fill('text', text)
        self.browser.find_by_css('#title').fill(title)
        self.browser.select('language_id', int(self.language_ids[langname]))
        self.browser.find_by_css('#save').first.click()

    def default_parsed_token_renderer(t):
        return t.text

    def text_and_status_renderer(t):
        classes = t['class'].split(' ')
        status_class = [c for c in classes if c.startswith('status')]
        if len(status_class) == 0:
            return t.text
        assert len(status_class) == 1, f'should only have 1 status on {t.text}'
        status = status_class[0].replace('status', '')
        return f'{t.text} ({status})'

    def displayed_text(self, token_renderer = default_parsed_token_renderer):
        "Return the TextItems, with '/' at token boundaries."
        elements = self.browser.find_by_xpath('//span[contains(@class, "textitem")]')
        etext = [ token_renderer(e) for e in elements ]
        return '/'.join(etext)

    def click_word_fill_form(self, word, updates = {}):
        elements = self.browser.find_by_xpath('//span[contains(@class, "textitem")]')
        es = [ e for e in elements if e.text == word ]
        assert len(es) > 0, f'match for {word}'
        es[0].click()
        with self.browser.get_iframe('wordframe') as iframe:
            if 'translation' in updates:
                iframe.find_by_css('#translation').fill(updates['translation'])
            if 'parents' in updates:
                for p in updates['parents']:
                    xp = 'ul#parentslist li.tagit-new > input.ui-autocomplete-input'
                    tagitbox = iframe.find_by_css(xp)
                    assert len(tagitbox) == 1, 'have parent input'
                    box = tagitbox.first
                    box.type(p, slowly=False)
                    box.type(Keys.RETURN)
                    time.sleep(0.1) # seconds
            iframe.find_by_css('#submit').first.click()

        # Have to refresh the content to query the dom ...
        # Unfortunately, I can't see how to refresh without reloading
        self.browser.reload()


@pytest.fixture(name='luteclient')
def fixture_lute_client(request, chromebrowser):
    """
    Start the lute browser.
    """
    useport = request.config.getoption("--port")
    if useport is None:
        # Need to specify the port, e.g.
        # pytest tests/acceptance --port=1234
        # Acceptance tests run using 'inv accept' sort this out automatically.
        pytest.exit("--port not set")
    c = LuteBrowser(chromebrowser, f'http://localhost:{useport}/')
    yield c


def test_hit_main_page(chromebrowser, request):
    "Hit the main page, sanity check only."
    useport = request.config.getoption("--port")
    url = f"http://localhost:{useport}/"
    chromebrowser.visit(url)
    assert chromebrowser.is_text_present('Lute'), 'have main page.'


def test_create_book(chromebrowser, luteclient):
    "Try creating a book."
    luteclient.visit('/')
    assert chromebrowser.is_text_present('Lute'), 'have main page.'
    luteclient.make_book('Hola', 'Hola. Adios amigo.', 'Spanish')
    assert chromebrowser.title == 'Reading "Hola (1/1)"', 'title'
    assert chromebrowser.is_text_present('Hola')
    assert 'Hola/. /Adios/ /amigo/.' == luteclient.displayed_text()

    updates = {
        'translation': 'hello',
        'parents': [ 'adios', 'amigo' ]
    }
    luteclient.click_word_fill_form('Hola', updates)
    luteclient.click_word_fill_form('Adios', { 'translation': 'goodbye' })

    displayed = luteclient.displayed_text(LuteBrowser.text_and_status_renderer)
    assert 'Hola (1)/. /Adios (1)/ /amigo (1)/.' == displayed
