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

## Using invoke for tasks

Lute3 uses [Invoke](https://docs.pyinvoke.org/en/stable/index.html) to run tasks.  Tasks are in `tasks.py`.

## Running in dev mode

The script `dev.py` runs the built-in Flask server in dev/debug mode.

For some reason, you have to supply the full path when running that file.  See that file's comments for notes.

e.g. for Mac:

```
# cd /path/to/lute3
python `pwd`/dev.py
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

Todos are in the code as comments, e.g.:

```
# TODO [<group name>:] detail
```

`inv todos` collects all of these in a simple report, eg:

```
-----------------
lute

Group: <None>
  ./read/render/renderable_calculator.py            :  Data structure for template read/textitem.html (TODO confirm template name)
  ./read/routes.py                                  :  # TODO: term form: ensure reading pane can create form with "." character
  ./models/book.py                                  :  todo for the future.
  ./templates/index.html                            :  <li style="color: grey;">Version and software info - TODO</li>
  ./templates/term/_form.html                       :  // TODO acceptance tests; need to check interactions.  Painful.
  ./templates/term/_form.html                       :  // TODO term form autofocus - check if used.
  ./templates/term/_form.html                       :  // TODO:fix_language_dict_asterisk
  ./templates/book/tablelisting.html                :  // TODO:security - add CSRF token
  ./templates/termtag/index.html                    :  // TODO:security - add CSRF token

Group: js data
  ./templates/base.html                             :  <!-- TODO js data: STATUS TAGS TEXTTAGS -->

Group: misc
  ./templates/base.html                             :  <!-- TODO misc: custom styles: add link -->

Group: parsers
  ./language/forms.py                               :  # TODO parsers: use the parser registry to load the select.
```

Keeping the TODOs standard simplifies the grepping, grouping, etc.