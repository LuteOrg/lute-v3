"""
Lute test client.

Convenience wrapper around the browser.

IMPORTANT: on start, clears db, and disables backup.

Adds the home url to visited urls,
provides common functions like make_book.

Also calls the dev_api to set state, etc.

This module is "registered" to pytest in ./__init__.py
to get nicer assertion details.
"""

import time
import json
import requests
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


class LuteTestClient:  # pylint: disable=too-many-public-methods
    """
    The client!
    """

    ################################3
    # Setup

    def __init__(self, b, home):
        self.browser = b
        self.home = home
        self.visit("dev_api/wipe_db")
        self.visit("dev_api/load_demo_languages")
        self.visit("dev_api/disable_backup")

        response = requests.get(f"{home}/dev_api/language_ids", timeout=5)
        self.language_ids = response.json()

        self.start = time.perf_counter()
        self.last_step = self.start

    def load_demo_stories(self):
        "Load the demo stories."
        self.visit("dev_api/load_demo_stories")
        self.visit("/")
        self.clear_book_filter()

    def change_parser_registry_key(self, key, replacement):
        """
        Change a parser registry key to a replacement,
        effectively disabling that parser.
        """
        self.visit(f"dev_api/disable_parser/{key}/{replacement}")

    ################################3
    # Browsing

    def visit(self, suburl):
        "Visit a sub url under the base."
        if suburl.startswith("/"):
            suburl = suburl[1:]
        url = f"{self.home}/{suburl}"
        # print(f'visiting: {url}')
        self.browser.visit(url)

    def index(self):
        "Go to home page."
        self.browser.visit("")

    def clear_book_filter(self):
        "Clear all state.  Normally state is saved."
        self.browser.execute_script("clear_datatable_state()")
        time.sleep(0.1)

    def click_link(self, linktext):
        self.browser.links.find_by_text(linktext).click()

    ################################3
    # Languages

    def edit_language(self, langname, updates=None):
        """
        Edit a language.
        """
        self.visit("/")
        self.browser.find_by_css("#menu_settings").mouse_over()
        self.browser.find_by_id("lang_index").first.click()
        # WEIRD: find_by_text(langname) doesn't work ...
        self.browser.links.find_by_partial_text(langname).click()
        assert f"Edit {langname}" in self.browser.html
        updates = updates or {}
        for k, v in updates.items():
            if k == "exceptions_split_sentences":
                self.browser.find_by_css(f"#{k}").fill(v)
            else:
                raise RuntimeError(f"unhandled key {k}")
        self.browser.find_by_css("#submit").first.click()

    ################################3
    # Books

    def make_book(self, title, text, langname):
        "Create a book with title, text, and languagename."
        self.visit("book/new")
        self.browser.fill("text", text)
        self.browser.find_by_css("#title").fill(title)
        self.browser.select("language_id", int(self.language_ids[langname]))
        self.browser.find_by_css("#save").first.click()

    def make_book_from_file(self, title, filename, langname):
        "Create a book with title, content from filename, and languagename."
        self.visit("book/new")
        self.browser.attach_file("textfile", filename)
        self.browser.find_by_css("#title").fill(title)
        self.browser.select("language_id", int(self.language_ids[langname]))
        self.browser.find_by_css("#save").first.click()

    def make_book_from_url(self, url, langname):
        "Create a book with title, content from url, and languagename."
        self.visit("book/import_webpage")
        self.browser.find_by_css("#importurl").fill(url)
        self.browser.find_by_css("#import").first.click()
        time.sleep(0.1)  # hack
        self.browser.select("language_id", int(self.language_ids[langname]))
        self.browser.find_by_css("#save").first.click()

    def get_book_table_content(self):
        "Get book table content."
        css = "#booktable tbody tr"

        # Skip the last two columns:
        # - "last opened" date is a hassle to check
        # - "actions" is just "..."
        def _to_string(row):
            tds = row.find_by_css("td")
            rowtext = [td.text.strip() for td in tds]
            ret = "; ".join(rowtext[:-2]).strip()
            # print(ret, flush=True)
            return ret

        rows = list(self.browser.find_by_css(css))
        return "\n".join([_to_string(row) for row in rows])

    def get_book_page_start_dates(self):
        "get content from sql check"
        sql = """select bktitle, txorder
        from books
        inner join texts on txbkid = bkid
        where txstartdate is not null
        order by bktitle, txorder"""
        response = requests.get(f"{self.home}/dev_api/sqlresult/{sql}", timeout=1)
        ret = "\n".join(json.loads(response.text))
        if ret == "":
            ret = "-"
        return ret

    def get_book_page_read_dates(self):
        "get content from sql check"
        sql = """select bktitle, txorder
        from books
        inner join texts on txbkid = bkid
        where txreaddate is not null
        order by bktitle, txorder"""
        response = requests.get(f"{self.home}/dev_api/sqlresult/{sql}", timeout=1)
        ret = "\n".join(json.loads(response.text))
        if ret == "":
            ret = "-"
        return ret

    def set_txstartdate_to_null(self):
        "hack back end to keep test data sane."
        sql = "update texts set txstartdate = null"
        response = requests.get(f"{self.home}/dev_api/execsql/{sql}", timeout=1)
        return response.text

    ################################
    # Terms

    def _fill_tagify_field(self, b, fieldid, text):
        "Fill in field in browser b with text."
        xpath = [
            # input w/ id
            f'//input[@id="{fieldid}"]',
            # <tags> before it.
            "/preceding-sibling::tags",
            # <span> within the <tags> with class.
            '/span[@class="tagify__input"]',
        ]
        xpath = "".join(xpath)

        # Sometimes test runs couldn't find the parent
        # tagify input, so hacky loop to get it and retry.
        span = None
        attempts = 0
        while span is None and attempts < 10:
            time.sleep(0.2)  # seconds
            attempts += 1
            span = b.find_by_xpath(xpath)
        if span is None:
            raise RuntimeError(f"unable to find {fieldid}")

        span.type(text, slowly=False)
        span.type(Keys.RETURN)
        time.sleep(0.3)  # seconds

    def _fill_term_form(self, b, updates):
        "Fill in the term form."
        for k, v in updates.items():
            if k == "language_id":
                b.select("language_id", v)
            elif k == "status":
                # This line didn't work:
                # iframe.choose('status', updates['status'])
                s = updates["status"]
                xp = "".join(
                    [
                        "//input[@type='radio'][@name='status']",
                        f"[@value='{s}']",
                        "/following-sibling::label",
                    ]
                )
                labels = b.find_by_xpath(xp)
                assert len(labels) == 1, "have matching radio button"
                label = labels[0]
                label.click()
            elif k in ("translation", "text", "romanization"):
                b.find_by_css(f"#{k}").fill(v)
            elif k in ("pronunciation"):
                b.find_by_css("#romanization").fill(v)
            elif k == "parents":
                for p in updates["parents"]:
                    self._fill_tagify_field(b, "parentslist", p)
            elif k == "sync_status":
                if v:
                    b.check("sync_status")
                else:
                    b.uncheck("sync_status")
            else:
                raise RuntimeError(f"unhandled key {k}")

    def _fill_bulk_term_edit_form(self, b, updates):
        "Fill in the term bulk edit form."
        for k, v in updates.items():
            if k == "remove parents":
                if v:
                    b.check("remove_parents")
                else:
                    b.uncheck("remove_parents")
            elif k == "parent":
                self._fill_tagify_field(b, "txtSetParent", v)
            elif k == "change status":
                if v:
                    b.check("change_status")
                else:
                    b.uncheck("change_status")
            elif k == "status":
                # This line didn't work:
                # iframe.choose('status', updates['status'])
                s = updates["status"]
                xp = "".join(
                    [
                        "//input[@type='radio'][@name='status']",
                        f"[@value='{s}']",
                        "/following-sibling::label",
                    ]
                )
                labels = b.find_by_xpath(xp)
                assert len(labels) == 1, "have matching radio button"
                label = labels[0]
                label.click()
            elif k in ("add tags", "remove tags"):
                fields = {"add tags": "txtAddTags", "remove tags": "txtRemoveTags"}
                for tag in updates[k].split(", "):
                    self._fill_tagify_field(b, fields[k], tag)
            else:
                raise RuntimeError(f"unhandled key {k}")

    def make_term(self, lang, updates):
        "Create a new term."
        # Sometimes this failed during the unsupported_parser.feature, not sure why.
        # Likely something silly, don't care, so will bypass the screen controls.
        # I am sure this will bite me later.
        # TODO fix_nav: figure out why occasionally got ElementNotInteractableException
        # self.visit("/")
        # self.browser.find_by_css("#menu_terms").mouse_over()
        # self.browser.find_by_id("term_index").first.click()
        # self.browser.find_by_css("#term_actions").mouse_over()
        # self.click_link("Create new")
        self.visit("/term/new")
        assert "New Term" in self.browser.html

        updates["language_id"] = self.language_ids[lang]
        b = self.browser
        self._fill_term_form(b, updates)
        b.find_by_css("#btnsubmit").first.click()

    def get_term_table_content(self):
        "Get term table content."
        self.visit("/")
        self.browser.find_by_css("#menu_terms").mouse_over()
        self.browser.find_by_id("term_index").first.click()

        # clear any filters!
        self.browser.find_by_id("showHideFilters").first.click()

        # The last column of the table is the "date added", but that's
        # a hassle to check, so ignore it.
        def _to_string(row):
            tds = row.find_by_css("td")
            rowtext = [td.text.strip() for td in tds]
            ret = "; ".join(rowtext).strip()
            if ret == "No data available in table":
                return ret
            return "; ".join(rowtext[:-1]).strip()

        css = "#termtable tbody tr"
        rows = list(self.browser.find_by_css(css))
        rowstring = [_to_string(row) for row in rows]
        return "\n".join(rowstring)

    ################################3
    # Reading/rendering

    def displayed_text(self):
        "Return the TextItems, with '/' at token boundaries."
        elements = self.browser.find_by_xpath('//span[contains(@class, "textitem")]')

        def _to_string(t):
            "Create string for token, eg 'cat (2)'."

            # Note that selenium's t.text accessor strips leading/trailing whitespace,
            # so if a span contains " ", t.text returns "".  We need the actual
            # inner html.
            # pylint: disable=protected-access
            inner_html = t._element.get_attribute("innerHTML")
            zws = "\u200B"
            inner_html = inner_html.replace(zws, "")

            status = [
                c.replace("status", "")
                for c in t["class"].split(" ")
                if c.startswith("status") and c != "status0"
            ]
            if len(status) == 0:
                return inner_html
            assert len(status) == 1, f"should only have 1 status on {inner_html}"
            return f"{inner_html} ({status[0]})"

        etext = [_to_string(e) for e in elements]
        ret = "/".join(etext)
        if ret.endswith("/"):
            ret = ret[:-1]
        return ret

    ################################3
    # Reading, term actions

    def _get_element_for_word(self, word):
        "Helper, get the element."
        # print('getting ' + word)
        elements = self.browser.find_by_xpath('//span[contains(@class, "textitem")]')
        es = [e for e in elements if e.text == word]
        assert len(es) > 0, f"match for {word}"
        return es[0]

    def click_word(self, word):
        "Click a word in the reading frame."
        self._get_element_for_word(word).click()

    def shift_click_words(self, words):
        "Shift-click words."
        # https://stackoverflow.com/questions/27775759/
        #   send-keys-control-click-in-selenium-with-python-bindings
        # pylint: disable=protected-access
        els = [self._get_element_for_word(w)._element for w in words]
        ac = ActionChains(self.browser.driver).key_down(Keys.SHIFT)
        for e in els:
            ac = ac.click(e)
        ac = ac.key_up(Keys.SHIFT)
        ac.perform()

    def shift_drag(self, fromword, toword):
        "Shift-drag over words."
        # https://stackoverflow.com/questions/27775759/
        #   send-keys-control-click-in-selenium-with-python-bindings
        # pylint: disable=protected-access
        [fromel, toel] = [
            self._get_element_for_word(w)._element for w in [fromword, toword]
        ]
        actions = ActionChains(self.browser.driver)
        actions.key_down(Keys.SHIFT)
        actions.click_and_hold(fromel)
        actions.move_to_element(toel)
        actions.key_up(Keys.SHIFT)
        actions.release()
        actions.perform()

    def drag(self, fromword, toword):
        "drag over words."
        # https://stackoverflow.com/questions/27775759/
        #   send-keys-control-click-in-selenium-with-python-bindings
        # pylint: disable=protected-access
        [fromel, toel] = [
            self._get_element_for_word(w)._element for w in [fromword, toword]
        ]
        actions = ActionChains(self.browser.driver)
        actions.click_and_hold(fromel)
        actions.move_to_element(toel)
        actions.release()
        actions.perform()

    def _refresh_browser(self):
        """
        Term actions (edits, hotkeys) cause updated content to be ajaxed in.
        For the splinter browser to be aware of it, the browser has to be
        reloaded, but calling a self.browser.reload() has other side effects
        (sets the page start date, etc).

        The below weird js hack causes the browser to be updated,
        and then the js events have to be reattached too.
        """
        # self.browser.reload()
        # ??? ChatGPT suggested:
        time.sleep(0.5)  # Hack for ci.
        self.browser.execute_script(
            """
            // Trigger re-render of the entire body
            var body = document.querySelector('body');
            var content = body.innerHTML;
            body.innerHTML = '';
            body.innerHTML = content;

            // Re-attach text interactions.
            window.prepareTextInteractions();
            """
        )
        time.sleep(0.5)  # Hack for ci.

    def fill_reading_bulk_edit_form(self, updates=None):
        """
        Click a word in the reading frame, fill in the term form iframe.
        """
        updates = updates or {}
        should_refresh = False
        with self.browser.get_iframe("wordframe") as iframe:
            time.sleep(0.4)  # Hack, test failing.
            self._fill_bulk_term_edit_form(iframe, updates)
            time.sleep(0.4)  # Hack, test failing.
            iframe.find_by_css("#btnsubmit").first.click()
            time.sleep(0.4)  # Hack, test failing.

            # Only refresh the reading frame if everything was ok.
            # Some submits will fail due to validation errors,
            # and we want to look at them.
            if "updated" in iframe.html:
                should_refresh = True

        # Have to refresh the content to query the dom.
        if should_refresh:
            self._refresh_browser()

    def hack_set_hotkey(self, hotkey, value):
        "Hack set hotkey directly through dev api.  Trashy."
        sql = f"""update settings
        set StValue='{value}' where StKey='{hotkey}'"""
        requests.get(f"{self.home}/dev_api/execsql/{sql}", timeout=1)
        # NOTE! Hacking is dumb, it bypassing the global state which is rendered in JS.
        # Have to visit and save settings to re-set the JS values that will be rendered.
        # Big time waste finding this out.
        self.visit("settings/shortcuts")
        self.browser.find_by_css("#btnSubmit").first.click()

    def press_hotkey(self, hotkey):
        "Send a hotkey."
        key_to_code_map = {
            "escape": "Escape",
            "1": "Digit1",
            "2": "Digit2",
            "3": "Digit3",
            "4": "Digit4",
            "5": "Digit5",
            "arrowdown": "ArrowDown",
            "arrowup": "ArrowUp",
            "h": "KeyH",
            "i": "KeyI",
            "m": "KeyM",
            "w": "KeyW",
            # Manually added.
            "8": "Digit8",
            "9": "Digit9",
        }
        if hotkey.lower() not in key_to_code_map:
            raise RuntimeError(f"Missing {hotkey} in acceptance test map")
        event_parts = [
            "type: 'keydown'",
            f"code: '{key_to_code_map[hotkey.lower()]}'",
        ]
        if hotkey != hotkey.lower():
            event_parts.append("shiftKey: true")
        script = f"""jQuery.event.trigger({{
          {', '.join(event_parts)}
        }});"""
        # print(script, flush=True)
        # pylint: disable=protected-access
        el = self.browser.find_by_id("thetext")
        self.browser.execute_script(script, el._element)
        time.sleep(0.2)  # Or it's too fast.
        # print(script)
        # Have to refresh the content to query the dom.
        self._refresh_browser()

    def click_word_fill_form(self, word, updates=None):
        """
        Click a word in the reading frame, fill in the term form iframe.
        """
        self.click_word(word)
        updates = updates or {}

        should_refresh = False
        with self.browser.get_iframe("wordframe") as iframe:
            time.sleep(0.4)  # Hack, test failing.
            self._fill_term_form(iframe, updates)
            time.sleep(0.4)  # Hack, test failing.
            iframe.find_by_css("#btnsubmit").first.click()
            time.sleep(0.4)  # Hack, test failing.

            # Only refresh the reading frame if everything was ok.
            # Some submits will fail due to validation errors,
            # and we want to look at them.
            if "updated" in iframe.html:
                should_refresh = True

        # Have to refresh the content to query the dom.
        if should_refresh:
            self._refresh_browser()

    ################################3
    # Misc.

    def elapsed(self, step):
        """
        Helper method for sorting out slowness.

        For the step, gives elapsed time since start of
        the LuteBrowser, and since the last recorded step.

        To see this data, run the acc. tests with '-s', eg:

        pytest tests/acceptance/test_smoke.py --port=5001 -s
        """
        now = time.perf_counter()
        since_start = now - self.start
        print(step)
        print(f"total elapsed: {since_start}")
        print(f"since last:    {now - self.last_step}")
        self.last_step = now

    def sleep(self, seconds):
        "Nap."
        time.sleep(seconds)

    def get_temp_file_content(self, filename):
        "Get book table content."
        response = requests.get(
            f"{self.home}/dev_api/temp_file_content/{filename}", timeout=1
        )
        return response.text
