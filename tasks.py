"""
Tasks to run using Invoke.

Ref https://docs.pyinvoke.org/en/stable/index.html

Samples:

invoke lint
invoke coverage --html

invoke --list          # list all tasks
invoke --help <cmd>    # See docstrings and help notes
"""

import os
from datetime import datetime
import pytest
from invoke import task, Collection

from lute.app_config import AppConfig
from lute.db.setup.main import setup_db


@task
def lint(c):
    "Run pylint on lute/ and tests/."
    # Formats: https://pylint.pycqa.org/en/latest/user_guide/usage/output.html
    msgfmt = "--msg-template='{path} ({line:03d}): {msg} ({msg_id} {symbol})'"
    c.run(f"pylint {msgfmt} lute/ tests/")


@task(help={'html': 'open html report'})
def coverage(c, html=False):
    """
    Run coverage, open report if needed.
    """
    c.run('coverage run -m pytest tests/')
    if html:
        c.run('coverage html --omit="*/test*"')
        c.run('open htmlcov/index.html')
    else:
        c.run('coverage report --omit="*/test*"')

@task
def todos(c):
    """
    Print code TODOs.
    """
    c.run('python utils/todos.py')

@task
def start(c):
    """
    Start the dev server, using script dev.py.
    """
    thisdir = os.path.dirname(os.path.realpath(__file__))
    devscript = os.path.join(thisdir, 'dev.py')
    c.run(f'python {devscript}')


@task
def resetstart(c):
    "Reset the db, and start the app."
    db_reset(c)
    start(c)


@task
def search(c, search_for):
    """
    Search the code for a string.
    """
    thisdir = os.path.dirname(os.path.realpath(__file__))
    devscript = os.path.join(thisdir, 'utils', 'findstring.sh')
    c.run(f'{devscript} "{search_for}"')


ns = Collection()
ns.add_task(lint)
ns.add_task(coverage)
ns.add_task(todos)
ns.add_task(start)
ns.add_task(resetstart)
ns.add_task(search)





##############################
# DB tasks

def _ensure_test_db():
    "Throw if not a testing db."
    ac = AppConfig.create_from_config()
    if ac.is_test_db is False:
        raise ValueError('not a test db')
    
@task
def db_wipe(c):
    """
    Wipe the data from the testing db; factory reset settings. :-)

    Can only be run on a testing db.
    """
    _ensure_test_db()
    c.run('pytest -m dbwipe')
    print('ok')


@task
def db_reset(c):
    """
    Reset the database to the demo data.

    Can only be run on a testing db.
    """
    _ensure_test_db()
    c.run('pytest -m dbdemoload')
    print('ok')


def _schema_dir():
    "Return full path to schema dir."
    thisdir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(thisdir, 'lute', 'db', 'schema')


def _do_schema_export(c, destfile, header_notes, taskname):
    """
    Generate the dumpfile at destfile.
    """
    destfile = os.path.join(_schema_dir(), destfile)
    tempfile = f'{destfile}.temp'
    commands = f"""
    echo "-- ------------------------------------------" > {tempfile}
    echo "-- {header_notes}" >> {tempfile}
    echo "-- Migrations tracked in _migrations, settings reset." >> {tempfile}
    echo "-- Generated from 'inv {taskname}'" >> {tempfile}
    echo "-- ------------------------------------------" >> {tempfile}
    echo "" >> {tempfile}
    sqlite3 data/test_lute.db .dump >> {tempfile}
    """
    c.run(commands)

    os.rename(tempfile, destfile)
    print(f'{destfile} updated (git diff follows):')
    print('DIFF START ' + '-' * 38)
    c.run(f'git diff -- {destfile}')
    print('DIFF END ' + '-' * 40)
    print()


@task
def db_export_baseline(c):
    """
    Reset the db, and create a new baseline db file from the current db.
    """

    # Running the delete task before this one as a pre- step was
    # causing problems (sqlite file not in correct state), so this
    # asks the user to verify.
    text = input(f'Have you reset the db?  (y/n): ')
    if (text != 'y'):
        print('quitting.')
        return
    _do_schema_export(c, 'baseline.sql', 'Baseline db with demo data.', 'db.export.baseline')

    fname = os.path.join(_schema_dir(), 'baseline.sql')
    print(f'Verifying {fname}')
    with open(fname) as f:
        checkstring = 'Tutorial follow-up'
        if checkstring in f.read():
            print(f'"{checkstring}" found, likely ok.')
        else:
            print(f'"{checkstring}" NOT FOUND, SOMETHING LIKELY WRONG.')
            raise RuntimeError(f'Missing "{checkstring}" in exported file.')


@task
def db_export_empty(c):
    """
    Create a new empty db file from the current db.
    
    This assumes that the current db is in data/test_lute.db.
    """

    # Running the delete task before this one as a pre- step was
    # causing problems (sqlite file not in correct state), so this
    # asks the user to verify.
    text = input(f'Have you **WIPED** the db?  (y/n): ')
    if (text != 'y'):
        print('quitting.')
        return
    _do_schema_export(c, 'empty.sql', 'EMPTY DB.', 'db.export.empty')


@task(help={'suffix': 'suffix to add to filename.'})
def db_newscript(c, suffix):
    """
    Create a new migration, <datetime>_suffix.sql
    """
    now = datetime.now()
    fnow = now.strftime('%Y%m%d_%H%M%S')
    filename = f'{fnow}_{suffix}.sql'
    destfile = os.path.join(_schema_dir(), 'migrations', filename)
    with open(destfile, 'w') as f:
        f.write('-- TODO - fill this in.')
    print('migration created:')
    print(destfile)


dbtasks = Collection('db')
dbtasks.add_task(db_reset, 'reset')
dbtasks.add_task(db_wipe, 'wipe')
dbtasks.add_task(db_newscript, 'newscript')
dbexport = Collection('export')
dbexport.add_task(db_export_baseline, 'baseline')
dbexport.add_task(db_export_empty, 'empty')
dbtasks.add_collection(dbexport)

ns.add_collection(dbtasks)
