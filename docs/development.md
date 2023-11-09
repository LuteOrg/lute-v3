# Development

> This may need revision, ping me if you need clarification as I wrote it quickly.

## Prereqs

* To work on Lute v3, you'll need at least Python 3.8 and pip.  You'll probably want to use some kind of virtual environments; I use venv and so will write that out here.
* Note that GitHub CI tests Python versions 3.8 through 3.11, as we can't be sure what version of Python users have, so stay away from newer language features.

## dependencies

Full (dev) dependencies are managed with pip:

`pip install <pkg>; pip freeze > requirements.txt`


## Setup and verify your dev environment

1. Clone as usual, checking out `master` (the current production branch).

2. set up your virtual environment, install all dev dependencies from requirements.txt, activate it:

```
python3.8 -m venv .venv
source .venv/bin/activate

# verify version
python --version

# Install requirements
pip install -r requirements.txt

# Install pre-commit hooks (optional, but recommended):
pre-commit install

deactivate
```

3. Copy `lute/config/config.yml.example` to `lute/config/config.yml`, making changes as you see fit.

If you're going to work on Lute, you're going to want to run unit tests.  The unit tests are **destructive**, in that they **wipe and reset the configured database.**

To guard against mistakes, the `DBNAME` in your config.yml must start with `test_`, `DATAPATH` must be set, and the `ENV` must be `dev`.  This *ensures* that you won't accidentally run the tests against your real Lute data.  I work with this by having two completely separate environments: one for dev work, and one for real Lute usage.  My prod data (actual data) stays in the latter.

4. Start lute up, ensure it's configured correctly

```
source .venv/bin/activate   # if necessary

python -m lute.main

# Open web browser to http://localhost:5000
# ... work work work ...
# When done, Ctl-C then
deactivate
```

5. Do initial run of all tests

Shut down your dev instance of Lute if it's running, and then run

```
inv full
```

to do a full pylint, test, and acceptance test run.  This should complete without errors, as lute master and develop branch are always kept passing in CI.

# Development

You may/may not find the overview docs of [Lute's architecture](./architecture.md) useful ... let me know.

## Commit hooks

Pre-commit hooks are installed with the `pre-commit install` step, and are run on every commit.  I find this useful, as it stops me from having to go back and clean up, but YMMV.  You can skip a step, e.g.: `SKIP=pylint git commit -m "Some non-lint-compliant commit."`

## Testing

Testing is done with pytest and pytest-bdd.  Run them as usual: `pytest`, `pytest -s`, `pytest -k test_setup`, `pytest -m somemark`, etc.

## `inv` or `invoke` for tasks

Lute3 uses [Invoke](https://docs.pyinvoke.org/en/stable/index.html) to run tasks.  Tasks are in `tasks.py`.  See `inv --list` for commands.

Some useful tasks:

| task | desc |
| --- | --- |
| inv start | start the app on a development Flask server in dev/debug mode |
| inv lint | lint |
| inv accept | start a running instance of the app server if needed, and run acceptance tests |

## Database changes

Database changes are _only_ managed through `lute.db.setup.migrator`.  To create a script, run `inv db.newscript <somesuffix>`, and edit the file to create a Sqlite-compliant change script.  See the existing scripts for examples.

## TODOs

Todos are in the code as comments, e.g. `# TODO [<group name>:] detail`, `<!-- TODO ... -->`.
`inv todos` collects all of these in a simple report.


# Docker

Notes for building and running a Docker container are at ../docker/README.com.

# Misc dev notes

## read-only db during tests

It _appears_ that killing acceptance tests mid-run results in a zombie (?) python process that keeps a handle on the db, causing it to get locked in read-only mode.

I couldn't find a better way to kill this process than do a full machine restart.  Sledgehammer approach that works.


## Acceptance tests suddenly failing

Worning during run of tests with `inv accept --exitfail`:

```
WARNING  selenium.webdriver.common.selenium_manager:selenium_manager.py:139 The chromedriver version (118.0.5993.70) detected in PATH at /opt/homebrew/bin/chromedriver might not be compatible with the detected chrome version (119.0.6045.105); currently, chromedriver 119.0.6045.105 is recommended for chrome 119.*, so it is advised to delete the driver in PATH and retry
```


```
brew upgrade chromedriver`
```

Then, on a Mac, have to "allow" it:

```
/opt/homebrew/bin/chromedriver --version
```

Will show message: "“chromedriver” can’t be opened because Apple cannot check it for malicious software."  Click "Show in Finder", then in Finder, click "Open" and say "OK" when it can't be verified.  Yes, this is a security risk.

# Packaging

TODO - need more notes here -- this probably belongs in a different document.

## Versioning

The current Lute version is specified in `lute/__init__.py`, and is pulled into the `pyproject.toml` using flit`s `dynamic` keyword.

Lute uses semver, `<major>`.`<minor>`.`<patch>`.

* `<major>` will likely stay at 3, as different modes (e.g. a thick client) will only be extensions of the current code.
* `<minor>` will increment on breaking DB schema changes, in case anyone writes scripts that directly hit the DB, or breaking API changes if and when an API is released.

This package will start at 0.0.1 until it's complete, and then will jump to 3.0.0.  Lute v1 and v2 were PHP projects, and Lute v3 is this Python rewrite.

## `pyproject.toml` dependencies

Lute uses `pyproject.toml` for packaging, and so the requirements are _also_ specified in the .toml file.

> **Note: I'm not experienced with pyproject.toml, so below is my current understanding.  In fact, I rather dislike the handling of dependencies in toml, as unpinned dependencies could create runtime issues.**

The full requirements are in requirements.txt, so use `pipdeptree` to pull out the requirements in a consumable fashion for the toml file:

```
pipdeptree --freeze
```

and then *manually* determine what should go into the `[project][dependencies]` and `dev`.

Note I take the requirements.txt `==` entries and change them to `>=x,<y`, assuming that future changes up until the next major release for that package are backwards-compatible.  E.g, the dependency for `Flask-SQLAlchemy==3.1.1` in requirements.txt becomes `Flask-SQLAlchemy>=3.1.1,<4`.

