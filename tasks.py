"""
Tasks to run using Invoke.

Ref https://docs.pyinvoke.org/en/stable/index.html

Samples:

invoke test
invoke test --print --args="-k test_main"
invoke lint
invoke coverage --html

invoke --list          # list all tasks
invoke --help <cmd>    # See docstrings and help notes
"""

import os
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

@task(help={'args': 'test arguments', 'print': 'include print statements'})
def test(c, args=None, print=False):
    """
    Run pytest.
    
    Sample calls:

    inv test
    inv test --args="-k test_main"
    inv test -a "-k test_main"
    inv test --print
    """
    runargs = [ 'tests' ]
    if args is not None:
        runargs.append(args)
    if print is True:
        runargs.append('-s')
    pytest.main(runargs)


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
def search(c, search_for):
    """
    Search the code for a string.
    """
    thisdir = os.path.dirname(os.path.realpath(__file__))
    devscript = os.path.join(thisdir, 'utils', 'findstring.sh')
    c.run(f'{devscript} "{search_for}"')


ns = Collection()
ns.add_task(lint)
ns.add_task(test)
ns.add_task(coverage)
ns.add_task(todos)
ns.add_task(start)
ns.add_task(search)





##############################
# DB tasks

@task
def db_reset(c):
    """
    Reset the database to the demo data. Can only be run on a testing db.

    It appears that doing this requires a restart of the dev server ...
    some file handle issue, I suppose.
    """
    ac = AppConfig.create_from_config()
    if ac.is_test_db is False:
        raise ValueError('not a test db')
    print(f'replacing {ac.dbfilename} with new demo db ...')
    os.unlink(ac.dbfilename)
    setup_db(ac)
    assert os.path.exists(ac.dbfilename)
    print('ok')


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

    thisdir = os.path.dirname(os.path.realpath(__file__))
    destfile = os.path.join(thisdir, 'lute', 'db', 'schema', 'baseline.sql')
    tempfile = f'{destfile}.temp'
    commands = f"""
    echo "-- ------------------------------------------" > {tempfile}
    echo "-- Baseline db with migrations and demo data." >> {tempfile}
    echo "-- Generated from 'inv db.export.baseline'" >> {tempfile}
    echo "-- ------------------------------------------" >> {tempfile}
    echo "" >> {tempfile}
    sqlite3 data/test_lute.db .dump >> {tempfile}
    """
    c.run(commands)

    print(f'Verifying {tempfile}')
    with open(tempfile) as f:
        checkstring = 'Tutorial follow-up'
        if checkstring in f.read():
            print(f'"{checkstring}" found, likely ok.')
        else:
            print(f'"{checkstring}" NOT found, something likely wrong.')
            raise RuntimeError(f'Missing "{checkstring}" in exported file.')

    os.rename(tempfile, destfile)
    print(f'{destfile} updated (git diff follows):')
    print('DIFF START ' + '-' * 38)
    c.run(f'git diff -- {destfile}')
    print('DIFF END ' + '-' * 40)
    print()


@task
def db_export_empty(c):
    """
    Create a new empty db file from the current db.
    
    This assumes that the current db is in data/test_lute.db.
    """
    thisdir = os.path.dirname(os.path.realpath(__file__))
    destfile = os.path.join(thisdir, 'lute', 'db', 'schema', 'empty.sql')
    commands = f"""
    echo "-- ------------------------------------------" > {destfile}
    echo "-- Empty db schema, with _migrations tracked." >> {destfile}
    echo "-- Generated from 'inv db.export.empty'" >> {destfile}
    echo "-- ------------------------------------------" >> {destfile}
    echo "" >> {destfile}
    sqlite3 data/test_lute.db .schema >> {destfile}
    echo "" >> {destfile}
    echo "-- -------------------------------------------" >> {destfile}
    echo "-- Migrations that have already been applied" >> {destfile}
    sqlite3 ../lute_dev/data/test_lute.db ".dump _migrations" >> {destfile}
    """
    c.run(commands)


dbtasks = Collection('db')
dbtasks.add_task(db_reset, 'reset')
dbexport = Collection('export')
dbexport.add_task(db_export_baseline, 'baseline')
dbexport.add_task(db_export_empty, 'empty')
dbtasks.add_collection(dbexport)

ns.add_collection(dbtasks)
