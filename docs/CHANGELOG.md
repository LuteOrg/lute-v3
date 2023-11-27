
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
