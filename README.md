# Lute v3

Using Python and Flask.

Work-in-progress.  TODO


# Requirements

Python 3

# Install

```
python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

deactivate
```

TODO:windows - get instructions from https://flask.palletsprojects.com/en/2.3.x/installation/ on venv


# Usage

> Note: this section is for usage when you clone the repo.

> TODO: notes about usage when installing from pre-packaged thing

* Copy lute/config/config.yml.example to lute/config/config.yml, making changes as you see fit
* Start the virtual environment, and run main:

```
source .venv/bin/activate   # if necessary

python -m lute.main

# Open web browser to http://localhost:5000
# ... work work work ...
# When done, Ctl-C then
deactivate
```


# Development

## Using invoke for tasks

Lute3 uses [Invoke](https://docs.pyinvoke.org/en/stable/index.html) to run tasks.  Tasks are in `tasks.py`.

## Running in dev mode

The script `devstart.py` runs the built-in Flask server in dev/debug mode.  Run it with either of these:

```
inv start
python -m devstart
```

## Testing

Testing is done with pytest and pytest-bdd.  Run them as usual:

```
pytest
pytest -s
pytest -k test_setup
pytest -m somemark
```

### Config

For tests, the lute/config/config.yml must have:

* `DBNAME` set to `test_<something>.db`
* `DATAPATH` set to some existing folder

## Commands

```
inv lint
inv coverage   # Coverage
```

See `inv --list` for commands.

## TODOs

Todos are in the code as comments, e.g. `# TODO [<group name>:] detail`, `<!-- TODO ... -->`.
`inv todos` collects all of these in a simple report.

# Versioning

Lute uses semver, `<major>`.`<minor>`.`<patch>`.

* `<major>` will likely stay at 3, as different modes (e.g. a thick
  client) will only be extensions of the current code.
* `<minor>` will increment on breaking DB schema changes, in case
  anyone writes scripts that directly hit the DB, or breaking API
  changes if and when an API is released!

This package will start at 0.0.1 until it's complete, and then will
jump to 3.0.0.  Lute v1 and v2 were PHP projects, and Lute v3 is this
Python rewrite.


# dependencies

## pip and requirements.txt

Full (dev) dependencies are managed with pip:

`pip install <pkg>; pip freeze > requirements.txt`

## `pyproject.toml`

> **Note: I'm not experienced with pyproject.toml, so below is my current understanding.  In fact, I rather dislike the handling of dependencies in toml, as unpinned dependencies could create runtime issues.**

Lute is an application, so it **appears** that the .toml file should only contain unpinned top-level dependencies.  I'm not sure about this!

The full requirements are in requirements.txt, so use `pipdeptree` to pull out the requirements in a consumable fashion for the toml file:

```
pipdeptree --freeze
```

and then *manually* determine what should go into the `[project][dependencies]` and `dev`.

Note I take the requirements.txt `==` entries and change them to `>=x,<y`, assuming that future changes up until the next major release for that package are backwards-compatible.  E.g, the dependency for `Flask-SQLAlchemy==3.1.1` in requirements.txt becomes `Flask-SQLAlchemy>=3.1.1,<4`.
