
# 3.2.7 (2024-03-15)

Feature changes:

* #325: Speed up homepage.
* #173: Speed up backups.
* #251: Show component terms of multi-word terms.
* Add zero-width joiners and non-joiners to some language definitions.  By @mrzaly in #334, #340
* #332: remove "bulk parent mapping"

Bug fixes:

* #329: fix term listing "select all" checkbox.
* Fix title and tooltip overflow.  By @imamcr in #323.

# 3.2.6 (2024-03-15)

Botched release: it included .mobi support from #338, subsequently pulled for 3.2.7.

# 3.2.5 (2024-03-13)

Feature changes:

* #84: Add SRT, VTT file imports.  By @imamcr in #320.
* #89: Add "add/remove" page operations to reading menu.  With nicer UI by @webofpies in #310.
* #272: Get book title from filename.  By @Jayanth-Parthsarathy in #322.
* #301: Saving new term in term listing stays on term form entry page.  By @Jayanth-Parthsarathy in #309.
* #305: Show date created in term listing page, include in CSV export.
* #312: Right-click on Lute logo to open new tab.  By @Jayanth-Parthsarathy in #314.

Bug fixes:

* #318: Fix broken links to docs.  By @mrzaly in #319.

Back end:

* #307: Move vendored css, js into separate folders in lute/static.  By @Jayanth-Parthsarathy in #308.
* Hacking at flaky tests.
* Remove unused static/iui


# 3.2.4 (2024-03-03)

Feature changes:

* #53: add "don't stop audio on term click" setting
* #295: add "open popups in new tab" setting
* #256: add "translate full page" reading menu link
* #209: Ctrl+Enter hotkey saves Term form while reading
* Fix Arabic and Chinese default dicts.  By @imamcr in #296, #298
* #199: Add delete audio button for book.
* #250: allow hide some book columns in listing.
* #288: open pop-up dictionary if it's the first dictionary specified

Bugfixes:

* #300: include pronunciation in csv export.

Back end changes:

* Update datatables to 2.0.1, include colvis.
* #289: make global js vars' relation to class explicit.


# 3.2.3 (2024-02-25)

Feature changes:

* #31: Using page break markers ("---") during new book creation only to force page breaks.
* #133: Set "current language" filter (and setting) from home page.
* #14: Allow term image uploads from keyboard or paste from clipboard.
* Add LWT and LingQ themes.  From @imamcr in #285.
* Fix touch-drag problem for mobile.  From @webofpies in #286.
* Small bug fixes.


# 3.2.2 (2024-02-21)

Feature changes:

* Move 'Export CSV' into term Actions menu.
* Issue #271: Fix multiword select in some text locations
* Issue #240: Use datatables for language listing.
* Issue #221: Don't scroll reading pane on term delete.
* Issue #269: Fix embedded translation dict.


# 3.2.1 (2024-02-19)

Feature changes:

* #238: add "Focus mode".  From @webofpies in #262, #268.
* #266: Add backup file download link.
* #237: Show last backup date, add listing.  By @sakolkar in #227.
* Improve dictionary UI, use tabs.  With @webofpies in #264.
* #5: Support variable number of dictionaries.
* #261: fix rtl language controls for book add, edit, page edit.
* #223: resize text areas horiz and vert.

Back end changes:

* schema, js changes for dictionary tabs.


# 3.1.4 (2024-02-11)

Feature changes:

* Issue 25: click term image and Delete/Backspace to delete.
* Issue 214: user must press Return to create parent tag.
* Issue 215: arrow changes status for hovered.
* Issue 213: no hovered elements if clicked.
* Issue 216: parent paste should show dropdown for hints.
* Show parent suggestions after single char input.


# 3.1.3 (2024-02-07)

Feature changes:

* [#182](https://github.com/jzohrab/lute-v3/issues/182): Confirm book archive.
* [#174](https://github.com/jzohrab/lute-v3/issues/174): Add bulk term deletion.
* [#205](https://github.com/jzohrab/lute-v3/issues/205): Add Actions menu to term listing to simplify adding actions.
* [#175](https://github.com/jzohrab/lute-v3/issues/175): Keep blank lines of imported texts when rendering page for reading.
* [#202](https://github.com/jzohrab/lute-v3/issues/202): Include all books in cli export.
* [#191](https://github.com/jzohrab/lute-v3/issues/191): Scroll back to top on "mark as read".
* [#177](https://github.com/jzohrab/lute-v3/issues/177): Show word count on book listing stats bar hover.
* [#164[(https://github.com/jzohrab/lute-v3/issues/164): Hit backspace to edit pasted parent tag.
* Add "(all)" to term status filter.
* [#166](https://github.com/jzohrab/lute-v3/issues/166): Keep returns in term translation in Terms listing.

Bug fixes:

* [#170](https://github.com/jzohrab/lute-v3/issues/170): Fix arrow keys for RTL languages.
* [#207](https://github.com/jzohrab/lute-v3/issues/207): Move title to right for RTL languages.

Back end changes:

* Simplify lute.js, remove state tracking


# 3.1.2 (2024-02-01)

* Bugfix: only recalc texts.TxWordCount for valid parsers.


# 3.1.1 (2024-01-30)

Feature changes:

* Add book stats graph and refresh.  By @webofpies in [154](https://github.com/jzohrab/lute-v3/pull/154) and [162](https://github.com/jzohrab/lute-v3/pull/162).
* [138](https://github.com/jzohrab/lute-v3/issues/138): Separate Word Count and % Known into separate columns and support sorting.
* Allow term listing search in translations.
* [155](https://github.com/jzohrab/lute-v3/issues/155): Add "words per page" field during book creation.  By @fanyingfx.

Bug fixes:

* [112](https://github.com/jzohrab/lute-v3/issues/112): show different options if backup failed (retry, skip, adjust settings)
* Sort statuses properly in the term listing.
* [95](https://github.com/jzohrab/lute-v3/issues/95): editing pages updates book word count
* Shorten migration file names to prevent Windows file path length exceptions

Misc back-end:

* Add term Export CSV test.
* Calc book stats on at least 5 pages.
* Clean up some form styles.
* Speed up book stats calculation.


# 3.1.0 (2024-01-22)

Feature changes:

* [#66](https://github.com/jzohrab/lute-v3/issues/66): add "Link to parent" checkbox for child terms to follow/change parent status
* Restyle radio buttons for nicer layout.  By @webofpies.

Back end changes:

* db schema and test changes for feature


# 3.0.12 (2024-01-18)

Feature changes:

* Improve term export: export all terms, change headings to be immediately importable.
* Add hotkeys to reading menu (pulled from manual).

Bugfixes:

* Fix sentences link.
* Fix spelling of "dismiss" in anchor tag for remove_demo_flag
* Fix scrolling bug on update.  By @webofpies.
* Fix z-index of player and popup.  By @webofpies in #127.

Back end changes:

* Change tagging library to tagify


# 3.0.11 (2024-01-11)

* rework/optimize form and table styles


# 3.0.10 (2024-01-10)

Feature changes:

* Make reading screen responsive, handles smaller viewports.  By @webofpies in #118.
* [#93](https://github.com/jzohrab/lute-v3/issues/93): add PDF imports.  By @dgc08 in #119.
* [#107](https://github.com/jzohrab/lute-v3/issues/107): fix Windows file locking on imports.


# 3.0.9 (2024-01-04)

Feature changes:

* [#29](https://github.com/jzohrab/lute-v3/issues/29): Add reading screen slider to navigate pages.  By @webofpies in #88.
* [#13](https://github.com/jzohrab/lute-v3/issues/13): Allow term deletion from reading screen.  By @disfated in #85.
* [#90](https://github.com/jzohrab/lute-v3/issues/90): Add Sanskrit.

Bug fixes:

* Remove duplicate terms from list (multiple image records) (addresses [#105](https://github.com/jzohrab/lute-v3/issues/105)).
* Graceful failure for non-utf-8 files (addresses [#67](https://github.com/jzohrab/lute-v3/issues/67)).
* Fix arrow key increment (addresses [#96](https://github.com/jzohrab/lute-v3/issues/96)).

Back end changes:

* Fix/disable flaky CI tests for reliability.
* Stats distribution field in db.


# 3.0.8 (2023-12-28)

Feature changes:

* Add .epub import (feature [19](https://github.com/jzohrab/lute-v3/issues/19)).  By @sakolkar in #82.
* Add resize frame option in reading pane.  By @webofpies in #77.
* Add "dismiss" demo option, for users who don't want to wipe the db.  By @dgc08 in #80.
* Nicer styling for the reading menu.  By @webofpies in #72.
* Add Hindi and example to baseline.  By @mzraly in #76.
* Update German sample story to new orthography.  By @dgc08 in #81.

Back end changes:

* Fix javascript attribute names to standard.  By @robby1066 in #79.
* Fix GitHub CI to really fail when things fail.
* Restructure book service to support epub import.


# 3.0.7 (2023-12-21)

Feature changes:

* Add slide-in menu for reading pane (issue [60](https://github.com/jzohrab/lute-v3/issues/60)).
* Add font/line spacing etc to slide-in menu (issue [45](https://github.com/jzohrab/lute-v3/issues/45)).
* Fix audio not loading reliably in Firefox.
* Keep book listing filter state on refresh (issue [46](https://github.com/jzohrab/lute-v3/issues/46)).
* Arrow keys only change status for clicked words, not hovered.
* Remove 'mark known' check on all pages, add 'make done' check on final page (issue [58](https://github.com/jzohrab/lute-v3/issues/58)).


# 3.0.6 (2023-12-13)

Feature changes:

* Add audio player to play mp3, wav, or ogg files.  See [docs](https://jzohrab.github.io/lute-manual/usage/audio.html)
* Add up/down arrow hotkey to change term status.
* Tweak Greek character range.
* Add 'is completed' check to book title in listing.

Supporting changes:

* Page content is now ajaxed in.


# 3.0.5 (2023-12-13)

(Skipped, botched release due to wifi problems.)


# 3.0.4 (2023-12-01)

* Fix sentence lookup for new term.


# 3.0.3 (2023-11-30)

Features and big fixes:

* Add read word count stats page.
* Bugfix: Only return sentence refs in same language.
* Add japanese automatic reading choices (katakana, hiragana, romaji)
* Add cert verification failure workaround message on 500 error.

Back-end changes:

* Break setting->JapaneseParser dependency.
* UserSetting mecab_path sets environ MECAB_PATH.
* Break ci dependency.


# 3.0.2 (2023-11-27)

* Add theming and highlight toggling.


# 3.0.1 (2023-11-23)

* [Issue 23](https://github.com/jzohrab/lute-v3/issues/23): paragraphs not rendered in correct order.
* Inject custom styles into other pages.


# 3.0.0 (2023-11-21)

Lute v3 launch.


# 3.0.0b11 (2023-11-19)

Feature changes:

* Add language term export command.
* Add czech language and demo story to baseline db.
* Bugfix: Respect the 'show pronunciation' lang setting in form.

Back end changes

* CLI command sketch.
* Use specified, root, or default config, in that order.
* Change create_app to take config file path, not object.
* Template for demo stories.


# 3.0.0b10 (2023-11-17)

Feature changes:

* Bugfix: Fix "archive book" broken link at end of book
* Issue 7: hotkey updates term form if displayed.
* Redirect to home if bad book id.
* Add custom 404 error handler.
* Change wiki refs on site to manual.
* Add Russian predefined language and story demo to baseline.


# 3.0.0b9 (2023-11-17)

* bugfix: parser type select box wasn't updating correctly.
* bugfix: Skip bad Japanese input tokens during parse.
* Multi-platform docker builds.
* Add nicer error handler.
* Allow change of mecab path, even in docker.

Back end changes:

* Remove MECAB_PATH from config file.
* Try different mecab path candidates if needed.



# 3.0.0b8 (2023-11-15)

* Add `--config` startup param for local prod dogfooding.

Back end changes:

* Simplify app config, attach to app.


# 3.0.0b7 (2023-11-14)

Feature changes:

* Fix sentence link.
* Fix mecab path manual references.


# 3.0.0b6 (2023-11-13)

* Fix image double-slash.


# 3.0.0b5 (2023-11-13)

Feature changes:

* Bugfix: missing default backup directory.
* Add container with margin to keep content off edges of screen.

Back end changes:

* Moved docs to wiki, easier to revise.
* Fix start task port.


# 3.0.0b4 (2023-11-12)

Feature changes:

* Add `--port` param to starter scripts, default is 5000.
* Load word reading if parser provides it.
* Add home link.


# 3.0.0b3 (2023-11-11)

Feature changes:

* Backups are on by default
* Set default backup dir.
* Add simple CSV export.
* Handling screen resizes better.

Back end changes:

* Docs
* Db baselining without settings
* Testing tweaks (e.g. no backup)
* Rename system backup dir.


# 3.0.0b1, b2 (2023-11-10)

Initial beta.
