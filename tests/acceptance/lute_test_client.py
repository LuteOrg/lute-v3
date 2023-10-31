"""
Lute test client.

Convenience wrapper around the browser, clears db.

Adds the home url to visited urls,
provides common functions like make_book.

Also calls the dev_api to set state, etc.
"""

import time
import requests
from selenium.webdriver.common.keys import Keys


class LuteTestClient:
    """
    The client!
    """
    def __init__(self, b, home):
        self.browser = b
        self.home = home
        self.visit('dev_api/wipe_db')
        self.visit('dev_api/load_demo_languages')

        response = requests.get(f'{home}/dev_api/language_ids', timeout=5)
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
        url = f'{self.home}/{suburl}'
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

    @staticmethod
    def default_parsed_token_renderer(t):
        return t.text

    @staticmethod
    def text_and_status_renderer(t):
        """
        Lambda, generate a string for a parsedtoken.

        Used to compare rendered content with expected.
        """
        ret = t.text

        classes = t['class'].split(' ')
        status_class = [c for c in classes if c.startswith('status')]
        if len(status_class) == 0:
            return ret
        assert len(status_class) == 1, f'should only have 1 status on {t.text}'

        status = status_class[0].replace('status', '')
        if status != '0':
            ret = f'{ret} ({status})'
        return ret


    def displayed_text(self, token_renderer = default_parsed_token_renderer):
        "Return the TextItems, with '/' at token boundaries."
        elements = self.browser.find_by_xpath('//span[contains(@class, "textitem")]')
        etext = [ token_renderer(e) for e in elements ]
        return '/'.join(etext)

    def click_word_fill_form(self, word, updates = None):
        """
        Click a word in the reading frame, fill in the term form iframe.
        """
        elements = self.browser.find_by_xpath('//span[contains(@class, "textitem")]')
        es = [ e for e in elements if e.text == word ]
        assert len(es) > 0, f'match for {word}'
        es[0].click()
        updates = updates or {}
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
