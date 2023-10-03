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

* Copy config/config.yml.example to config/config.yml, making changes as you see fit
* Start the virtual environment, and run main:

```
source .venv/bin/activate   # if necessary
python main.py
```

# When done, Ctl-C then

```
deactivate
```

* Open web browser to http://localhost:5000

# Development

TODO notes

## Running in dev mode

The script `dev.py` runs the built-in Flask server in dev/debug mode.

For some reason, you have to supply the full path when running that file.  See that file's comments for notes.

e.g. for Mac:

```
# cd /path/to/lute3
python `pwd`/dev.py
```

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
