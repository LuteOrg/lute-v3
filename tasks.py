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

from invoke import task
import pytest

@task(help={'clean': 'clean message'})
def hello(c, clean=False):
    "Say hi"
    print("Hello!")

@task
def lint(c):
    "Run pylint on lute/ and tests/."
    c.run("pylint lute/ tests/")

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
