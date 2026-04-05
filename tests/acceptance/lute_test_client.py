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
from playwright.sync_api import Keyboard, Mouse, expect


class LuteTestClient:  # pylint: disable=too-many-public-methods
    """
    The client!
    """

    ################################3
    # Setup

    def __init__(self, p, home, has_touch=False):
        self.has_touch = has_touch
        self.page = p
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
        if suburl.startswith(self.home):
            url = suburl
        else:
            url = f"{self.home}/{suburl}"
        # print(f'visiting: {url}')
        self.page.goto(url)

    def index(self):
        "Go to home page."
        self.visit("")

    def clear_book_filter(self):
        "Clear all state.  Normally state is saved."
        self.page.evaluate("clear_datatable_state()")
        time.sleep(0.1)

    def click_link(self, linktext):
        self.page.locator(f'text="{linktext}"').click()

    ################################3
    # Languages

    def edit_language(self, langname, updates=None):
        """
        Edit a language.
        """
        self.visit("/")
        self.page.hover("#menu_settings")
        self.page.locator("#lang_index").first.click()

        # Partial text match for link
        self.page.get_by_role("link", name=langname, exact=False).click()
        time.sleep(0.1)  # hack
        assert f"Edit {langname}" in self.page.content()

        updates = updates or {}
        for k, v in updates.items():
            if k == "exceptions_split_sentences":
                self.page.locator(f"#{k}").fill(v)
            else:
                raise RuntimeError(f"unhandled key {k}")

        self.page.click("#submit")

    ################################3
    # Books

    def make_book(self, title, text, langname):
        "Create a book with title, text, and languagename."
        self.visit("book/new")
        self.page.fill('textarea[name="text"]', text)  # assuming <textarea name="text">
        self.page.fill("#title", title)
        self.page.select_option(
            'select[name="language_id"]', str(self.language_ids[langname])
        )
        # Without force=True, was getting an error:
        # "<td>…</td> from <table id="book">…</table> subtree intercepts pointer events".
        # TODO fix_test: "force=True" is hacky as it can obscure layout problems.
        self.page.locator("#save").click(force=True)

    def make_book_from_file(self, title, filename, langname):
        "Create a book with title, content from filename, and languagename."
        self.visit("book/new")
        file_input = self.page.locator('input[type="file"][name="textfile"]')
        file_input.set_input_files(filename)
        self.page.fill("#title", title)
        self.page.select_option(
            'select[name="language_id"]', str(self.language_ids[langname])
        )
        self.page.locator("#save").click(force=True)

    def make_book_from_url(self, url, langname):
        "Create a book with title, content from url, and languagename."
        self.visit("book/import_webpage")
        self.page.fill("#importurl", url)
        self.page.locator("#import").click()
        time.sleep(0.1)  # hack
        self.page.select_option(
            'select[name="language_id"]', str(self.language_ids[langname])
        )
        self.page.locator("#save").click(force=True)

    def get_book_table_content(self):
        "Get book table content."
        rows = self.page.locator("#booktable tbody tr")
        rowcount = rows.count()
        content = []

        for i in range(rowcount):
            row = rows.nth(i)
            tds = row.locator("td")
            tdcount = tds.count()
            rowtext = [tds.nth(j).inner_text().strip() for j in range(tdcount)]
            # Skip the last two columns:
            # - "last opened" date is a hassle to check
            # - "actions" is just "..."
            ret = "; ".join(rowtext[:-2]).strip()
            # Hacky cleanup ok for tests.
            ret = ret.replace("\u200B", "").replace("\n", "").replace("\\n", "")
            content.append(ret)

        return "\n".join([c for c in content if c.strip() != ""]).strip()

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

    def _fill_tagify_field(self, frame, fieldid, text):
        "Fill a Tagify field inside `frame` with `text`."

        xpath = (
            f'//input[@id="{fieldid}"]'
            "/preceding-sibling::tags"
            '/span[contains(@class, "tagify__input")]'
        )

        span = None
        attempts = 0
        while span is None and attempts < 10:
            time.sleep(0.2)
            attempts += 1
            elements = frame.locator(f"xpath={xpath}")
            if elements.count() > 0:
                span = elements.nth(0)

        if span is None:
            raise RuntimeError(f"unable to find {fieldid}")

        # Focus the span and type text.  Various timing hacks added to
        # ensure that tagify wires things up correctly in response to
        # clicks ...  hacky, but fixed errors during ci runs.
        expect(span).to_be_visible()
        expect(span).to_be_enabled()
        span.click()
        time.sleep(0.1)
        expect(span).to_be_focused()
        time.sleep(0.1)
        span.fill(text)
        time.sleep(0.1)
        span.press("Enter")
        time.sleep(0.3)

    def _fill_term_form(self, page, updates):
        "Fill in the term form."
        for k, v in updates.items():
            if k == "language_id":
                page.select_option("select[name='language_id']", str(v))

            elif k == "status":
                s = updates["status"]
                x = f"//input[@type='radio'][@name='status'][@value='{s}']/following-sibling::label"
                labels = page.locator(f"xpath={x}")
                count = labels.count()
                assert count == 1, "have matching radio button"
                labels.nth(0).click()

            elif k in ("translation", "text", "romanization"):
                page.fill(f"#{k}", v)

            elif k == "pronunciation":
                page.fill("#romanization", v)

            elif k == "parents":
                for p in updates["parents"]:
                    self._fill_tagify_field(page, "parentslist", p)

            elif k == "sync_status":
                checkbox = page.locator("input[name='sync_status']")
                checked = checkbox.is_checked()
                if v and not checked:
                    checkbox.check()
                elif not v and checked:
                    checkbox.uncheck()

            else:
                raise RuntimeError(f"unhandled key {k}")

    def _fill_bulk_term_edit_form(self, frame, updates):
        "Fill in the term bulk edit form using Playwright."
        for k, v in updates.items():
            # print(f"Bulk form, updating {k} to {v}", flush=True)
            if k == "remove parents":
                cb = frame.locator("#chkRemoveParents")
                if v:
                    cb.check()
                else:
                    cb.uncheck()
            elif k == "parent":
                self._fill_tagify_field(frame, "txtSetParent", v)
            elif k == "change status":
                cb = frame.locator("#chkChangeStatus")
                if v:
                    cb.check()
                else:
                    cb.uncheck()
            elif k == "status":
                s = updates["status"]
                xp = (
                    f"//input[@type='radio'][@name='status'][@value='{s}']"
                    "/following-sibling::label"
                )
                labels = frame.locator(f"xpath={xp}")
                assert labels.count() == 1, "have matching radio button"
                labels.first.click()
            elif k in ("add tags", "remove tags"):
                fields = {"add tags": "txtAddTags", "remove tags": "txtRemoveTags"}
                for tag in updates[k].split(", "):
                    self._fill_tagify_field(frame, fields[k], tag)
            else:
                raise RuntimeError(f"unhandled key {k}")

    def make_term(self, lang, updates):
        "Create a new term."
        self.visit("/term/new")
        assert "New Term" in self.page.content()

        updates["language_id"] = self.language_ids[lang]
        self._fill_term_form(self.page, updates)
        self.page.click("#btnsubmit")

    def get_term_table_content(self):
        "Get term table content."
        self.visit("/")

        self.page.hover("#menu_terms")
        self.page.click("#term_index")

        # Clear any filters
        self.page.click("#showHideFilters")

        # The last column ("date added") is skipped, as in Splinter version
        rows = self.page.query_selector_all("#termtable tbody tr")

        rowstring = []

        def _delimited_tags(td):
            """Get the cleaned tags."""
            # print(f"GOT RAW TAGS = {td.inner_text()}", flush=True)
            tags = [t.strip() for t in td.inner_text().split("\n")]
            tags = [t for t in tags if t not in ["", "\u200B"]]
            return ", ".join(tags)

        for row in rows:
            tds = row.query_selector_all("td")
            rowtext = [td.inner_text().strip() for td in tds]
            check = "; ".join(rowtext).strip()

            if check == "No data available in table":
                rowstring.append(check)
                continue

            rowtext = [""]  # first column is an empty checkbox
            rowtext.append(tds[1].inner_text().strip())  # term

            rowtext.append(_delimited_tags(tds[2]))  # parent terms

            rowtext.append(tds[3].inner_text().strip())  # translation
            rowtext.append(tds[6].inner_text().strip())  # language

            rowtext.append(_delimited_tags(tds[4]))  # term tags

            select_element = row.query_selector("select")
            selected_value = select_element.input_value()
            selected_option = select_element.query_selector(
                f'option[value="{selected_value}"]'
            )
            selected_text = (
                selected_option.inner_text().strip() if selected_option else ""
            )
            rowtext.append(selected_text)

            # Hacky cleanup, ok for tests.
            # print(f"RAW ROWTEXT = {rowtext}", flush=True)
            rowtext = [
                r.replace("\u200B", "").replace("\n", "").replace("\\n", "")
                for r in rowtext
            ]
            rowval = "; ".join(rowtext).strip()
            rowstring.append(rowval)

        # print(f"RAW ROWSTRINGs = {rowstring}", flush=True)
        return "\n".join([r for r in rowstring if r.strip() != ""]).strip()

    ################################3
    # Reading/rendering

    def displayed_text(self):
        "Return the TextItems, with '/' at token boundaries."
        self.page.wait_for_selector('span[class*="textitem"]')
        elements = self.page.query_selector_all('span[class*="textitem"]')
        # print("check elements on page", flush=True)
        # print(elements, flush=True)

        def _to_string(t):
            "Create string for token, eg 'cat (2)'."
            zws = "\u200B"
            inner_html = t.inner_html().replace(zws, "")

            class_attr = t.get_attribute("class") or ""
            status = [
                c.replace("status", "")
                for c in class_attr.split(" ")
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
        self.page.wait_for_selector('span[class*="textitem"]')
        elements = self.page.query_selector_all('span[class*="textitem"]')
        es = [e for e in elements if e.text_content() == word]
        assert len(es) > 0, f"match for {word}"
        # print(f"got match for {word}", flush=True)
        return es[0]

    def click_word(self, word):
        "Click a word in the reading frame."
        el = self._get_element_for_word(word)
        # print(f"got element {el}", flush=True)
        if self.has_touch:
            el.tap()
        else:
            el.click()

    def shift_click_words(self, words):
        "Shift-click words."
        els = [self._get_element_for_word(w) for w in words]
        self.page.keyboard.down("Shift")
        for e in els:
            e.click()
        self.page.keyboard.up("Shift")

    def shift_drag(self, fromword, toword):
        "Shift-drag over words."
        from_el = self._get_element_for_word(fromword)
        to_el = self._get_element_for_word(toword)

        # Get bounding boxes for precise mouse control
        from_box = from_el.bounding_box()
        to_box = to_el.bounding_box()

        assert from_box and to_box, "Element bounding boxes must exist"

        # Press Shift, click and drag
        kb: Keyboard = self.page.keyboard
        mouse: Mouse = self.page.mouse

        kb.down("Shift")
        mouse.move(
            from_box["x"] + from_box["width"] / 2,
            from_box["y"] + from_box["height"] / 2,
        )
        mouse.down()
        mouse.move(
            to_box["x"] + to_box["width"] / 2, to_box["y"] + to_box["height"] / 2
        )
        mouse.up()
        kb.up("Shift")

    def drag(self, fromword, toword):
        "drag over words."
        from_el = self._get_element_for_word(fromword)
        to_el = self._get_element_for_word(toword)

        # Get bounding boxes for precise mouse control
        from_box = from_el.bounding_box()
        to_box = to_el.bounding_box()
        assert from_box and to_box, "Element bounding boxes must exist"
        mouse: Mouse = self.page.mouse
        mouse.move(
            from_box["x"] + from_box["width"] / 2,
            from_box["y"] + from_box["height"] / 2,
        )
        mouse.down()
        mouse.move(
            to_box["x"] + to_box["width"] / 2, to_box["y"] + to_box["height"] / 2
        )
        mouse.up()

    def _refresh_browser(self):
        """
        Term actions (edits, hotkeys) cause updated content to be ajaxed in.
        For the page to be aware of it, the page has to be
        reloaded, but calling a self.page.reload() has other side effects
        (sets the page start date, etc).

        The below weird js hack causes the page to be updated,
        and then the js events have to be reattached too.
        """
        # self.browser.reload()
        # ??? ChatGPT suggested:
        time.sleep(0.2)  # Hack for ci.
        self.page.evaluate(
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
        time.sleep(0.2)  # Hack for ci.

    def fill_reading_bulk_edit_form(self, updates=None):
        """
        Click a word in the reading frame, fill in the term form iframe.
        """
        updates = updates or {}
        should_refresh = False
        iframe = self.page.frame(name="wordframe")
        time.sleep(0.2)  # Hack, test failing.
        self._fill_bulk_term_edit_form(iframe, updates)
        time.sleep(0.2)  # Hack, test failing.
        iframe.locator("#btnsubmit").first.click()
        time.sleep(0.2)  # Hack, test failing.

        # Only refresh the reading frame if everything was ok.
        # Some submits will fail due to validation errors,
        # and we want to look at them.
        if "updated" in iframe.content():
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
        self.page.click("#btnSubmit")

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
        el = self.page.locator("#thetext")
        self.page.evaluate(script, el)
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
        iframe = self.page.frame(name="wordframe")
        time.sleep(0.2)  # Hack, test failing.
        self._fill_term_form(iframe, updates)
        time.sleep(0.2)  # Hack, test failing.
        iframe.locator("#btnsubmit").first.click()
        time.sleep(0.2)  # Hack, test failing.

        # Only refresh the reading frame if everything was ok.
        # Some submits will fail due to validation errors,
        # and we want to look at them.
        if "updated" in iframe.content():
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
