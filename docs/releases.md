# Releases

> These notes need some revision, but the idea is there.
> Some of the points from the lutev2 making_a_release.md need to be pulled in here as well.

The release process:

## 1. Test and re-baseline

```
inv full
inv db.reset
inv db.export.baseline
```

## 2. Bump version to x.y.z.dev1

See "Versioning" below.

Version is in `lute/__init__.py`

## 3. Pre-release to testpypi, testing

The pre-release to testpypi uncovers any packaging issues.

```
# from lute-v3 dir
flit publish --repository testpypi
```

Then, from other folder, in a _new process_ to get a new venv:

```
cd lute-v3-test
deactivate
rm -rf .venv
python3.8 -m venv .venv
source .venv/bin/activate

# `lute3` has dependencies on packages that aren't in TestPyPi,
# so we have to pull some things from PyPi as well.
# Note if it's a pre-release, you have to specify the *full value* of the tag
pip install --upgrade -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ lute3==3.0.0a1.dev1

# Run and check
python -m lute.main
# ... Ctl-C when done

deactivate
```

## 4. Bump version to final value x.y.z

Version is in `lute/__init__.py`

## 5. Release to pypi and check

flit publish --repository pypi

```
cd lute-v3-test
deactivate
rm -rf .venv
python3.8 -m venv .venv
source .venv/bin/activate
pip install lute3
python -m lute.main
# check
# Ctl-C
```

## 6. Tag and push to GitHub

> have to think about when to do this a bit more, also tagging

## 7. Release to docker hub

DO_PUSH=1 ./docker/build_all.sh

## 8. Announcements

On Discord etc.


# Versioning

Lute follows the version notes in https://packaging.python.org/en/latest/specifications/version-specifiers/#version-specifiers

The current Lute version is specified in `lute/__init__.py`, and is pulled into the `pyproject.toml` using flit`s `dynamic` keyword.  Lute uses something like, `<major>`.`<minor>`.`<patch>`.

* `<major>` will likely stay at 3, as different modes (e.g. a thick client) will only be extensions of the current code.
* `<minor>` will increment on breaking DB schema changes, in case anyone writes scripts that directly hit the DB, or breaking API changes if and when an API is released.

# `pyproject.toml` dependencies

Lute uses `pyproject.toml` for packaging, and so the requirements are _also_ specified in the .toml file.

> **Note: I'm not experienced with pyproject.toml, so below is my current understanding.  In fact, I rather dislike the handling of dependencies in toml, as unpinned dependencies could create runtime issues.**

The full requirements are in requirements.txt, so use `pipdeptree` to pull out the requirements in a consumable fashion for the toml file:

```
pipdeptree --freeze
```

and then *manually* determine what should go into the `[project][dependencies]` and `dev`.

Note I take the requirements.txt `==` entries and change them to `>=x,<y`, assuming that future changes up until the next major release for that package are backwards-compatible.  E.g, the dependency for `Flask-SQLAlchemy==3.1.1` in requirements.txt becomes `Flask-SQLAlchemy>=3.1.1,<4`.

