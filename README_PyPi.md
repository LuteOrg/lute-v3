# `lute3`

Learning Using Texts v3.

Lute v3 is a rewrite of the original Lute PHP application in Python and Flask.

<!-- TODO release: update/complete pypi readme documentation -->

## Requirements

Python 3.8+

## Install

### From PyPi

TODO release: add PyPi docs

### From TestPyPi

`lute3` is on TestPyPi to work out packaging issues.

`lute3` has dependencies on packages that aren't in TestPyPi, so we have to pull some things from PyPi as well.

```
python3 -m venv .venv
source .venv/bin/activate
pip3 install --upgrade --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ lute3
deactivate
```

## Usage

Assuming you've set up a virtual environment and installed `lute3`:

```
source .venv/bin/activate
python -m lute3.main

# Open web browser to http://localhost:5000
# ... work work work ...
# When done, Ctl-C then

deactivate
```
