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

TODO

## Testing

### Config

For tests, the config/config.yml must have:

* `DBNAME` set to `test_<something>.db`
* `DATAPATH` set to some existing folder

### Commands

```
# Run all
make test        # python -m pytest

# Run all and see any print statements
make testprint   # python -m pytest -s

# Run specific
ARGS="-k test_setup" make test

# or if working on a specific test:
export ARGS="-k test_setup"
make test
export ARGS=""  # when done
```
