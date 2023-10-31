"""
Smoke tests.
"""

import requests
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
        print('got ids:')
        print(self.language_ids)


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


@pytest.fixture(name='luteclient')
def fixture_lute_client(browser):
    """
    Start the lute browser.
    """
    c = LuteBrowser(browser, 'http://localhost:9876/')
    yield c


def test_hit_main_page(browser):
    "Hit the main page, sanity check only."
    url = "http://localhost:9876/"
    browser.visit(url)
    assert browser.is_text_present('Lute'), 'have main page.'


def test_create_book(browser, luteclient):
    "Try creating a book."
    luteclient.visit('/')
    assert browser.is_text_present('Lute'), 'have main page.'
    luteclient.make_book('hello', 'here is a super book.', 'English')
    assert browser.is_text_present('super')
