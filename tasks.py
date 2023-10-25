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

from invoke import task, Collection
import pytest

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

ns = Collection()
ns.add_task(lint)
ns.add_task(test)
ns.add_task(coverage)
ns.add_task(todos)
    
@task
def db_export_baseline(c):
    """
    Create a new baseline db file from the current db.
    
    This assumes that the current db is in data/test_lute.db.
    """
    print('TODO: reset the db data.')


@task
def db_export_empty(c):
    """
    Create a new empty db file from the current db.
    
    This assumes that the current db is in data/test_lute.db.
    """
    destfile = 'lute/db/schema/empty.sql'
    c.run(f'sqlite3 data/test_lute.db .schema > {destfile}')
    c.run(f'echo "" >> {destfile}')
    c.run(f'echo "###########################################" >> {destfile}')
    c.run(f'echo "# Migrations that have already been applied" >> {destfile}')
    c.run(f'sqlite3 ../lute_dev/data/test_lute.db ".dump _migrations" >> {destfile}')


dbtasks = Collection('db')
dbexport = Collection('export')
dbexport.add_task(db_export_baseline, 'baseline')
dbexport.add_task(db_export_empty, 'empty')
dbtasks.add_collection(dbexport)

ns.add_collection(dbtasks)
