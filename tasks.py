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
import sys
import subprocess
from datetime import datetime
import requests
from invoke import task, Collection
from lute.config.app_config import AppConfig


@task
def lint(c):
    "Run pylint on lute/ and tests/."
    # Formats: https://pylint.pycqa.org/en/latest/user_guide/usage/output.html
    msgfmt = "--msg-template='{path} ({line:03d}): {msg} ({msg_id} {symbol})'"
    c.run(f"pylint {msgfmt} tasks.py lute/ tests/")


@task
def todos(c):
    """
    Print code TODOs.
    """
    c.run("python utils/todos.py")


@task(help={"port": "optional port to run on; default = 5000"})
def start(c, port=5000):
    """
    Start the dev server, using script dev.py.
    """
    c.run(f"python -m devstart --port {port}")


@task
def search(c, search_for):
    """
    Search the code for a string.
    """
    thisdir = os.path.dirname(os.path.realpath(__file__))
    devscript = os.path.join(thisdir, "utils", "findstring.sh")
    c.run(f'{devscript} "{search_for}"')


@task
def _ensure_test_db(c):  # pylint: disable=unused-argument
    "Quits if not a test db. (Hidden task)"
    ac = AppConfig(AppConfig.default_config_filename())
    if ac.is_test_db is False:
        print(
            f"""
        QUITTING TASK FOR NON-TEST DB.
        Your database name must start with test_ to run this task.
        Your config.yml file has dbname = {ac.dbname}.
        """
        )
        sys.exit(1)


@task(pre=[_ensure_test_db])
def test(c):
    """
    Unit tests only.
    """
    c.run("pytest --ignore=./tests/acceptance")


def _site_is_running(useport=None):
    """
    Return true if site is running on port, or default 5000.
    """
    if useport is None:
        useport = 5000

    url = f"http://localhost:{useport}"
    try:
        print(f"checking for site at {url} ...")
        resp = requests.get(url, timeout=5)
        if resp.status_code != 200:
            raise RuntimeError(f"Got code {resp.status_code} ... ???")
        print("Site running, using that for tests.")
        print()
        return True
    except requests.exceptions.ConnectionError:
        print(f"URL {url} not reachable, will start new server at that port.")
        print()
        return False


@task(
    pre=[_ensure_test_db],
    help={
        "port": "optional port to run on; creates server if needed.",
        "show": "print data",
        "noheadless": "run as non-headless (default is headless, i.e. not shown)",
        "kflag": "optional -k flag argument",
        "exitfirst": "exit on first failure",
        "verbose": "make verbose",
    },
)
def accept(  # pylint: disable=too-many-arguments
    c,
    port=5000,
    show=False,
    noheadless=False,
    kflag=None,
    exitfirst=False,
    verbose=False,
):
    """
    Start lute, run tests/acceptance tests, screenshot fails.

    If no port specified, use default 5000.

    If Lute's not running on specified port, start a server.
    """
    run_test = [
        "pytest",
        "tests/acceptance",
        "--splinter-screenshot-dir=tests/acceptance/failure_screenshots",
        "--splinter-webdriver=chrome",
        f"--port={port}",
    ]

    if show:
        run_test.append("-s")
    if not noheadless:
        run_test.append("--headless")
    if kflag:
        run_test.append("-k")
        run_test.append(kflag)
    if exitfirst:
        run_test.append("--exitfirst")
    if verbose:
        run_test.append("-vv")

    tests_failed = False
    if _site_is_running(port):
        c.run(" ".join(run_test))
    else:
        cmd = ["python", "-m", "tests.acceptance.start_acceptance_app", f"{port}"]
        with subprocess.Popen(cmd) as app_process:
            try:
                subprocess.run(run_test, check=True)
            except subprocess.CalledProcessError:
                # This just means a test failed.  We don't need to see
                # a stack trace, the assert failures are already displayed.
                tests_failed = True
            finally:
                app_process.terminate()

    if tests_failed:
        raise RuntimeError("tests failed")


@task(pre=[_ensure_test_db])
def playwright(c):
    """
    Start lute, run playwright tests.  export SHOW=true env var to run non-headless.

    Only uses port 5000.

    If Lute's not running on specified port, start a server.
    """
    run_test = ["pytest", "tests/playwright/playwright.py", "-s"]

    tests_failed = False
    port = 5000
    if _site_is_running(port):
        c.run(" ".join(run_test))
    else:
        cmd = ["python", "-m", "tests.acceptance.start_acceptance_app", f"{port}"]
        with subprocess.Popen(cmd) as app_process:
            try:
                subprocess.run(run_test, check=True)
            except subprocess.CalledProcessError:
                # This just means a test failed.  We don't need to see
                # a stack trace, the assert failures are already displayed.
                tests_failed = True
            finally:
                app_process.terminate()

    if tests_failed:
        raise RuntimeError("tests failed")


@task(pre=[_ensure_test_db], help={"html": "open html report"})
def coverage(c, html=False):
    """
    Run coverage (using non-acceptance tests only), open report if needed.

    Running tests including the acceptance tests is slow,
    and doesn't affect the coverage stats enough to justify it.
    """
    c.run("coverage run -m pytest tests/")
    if html:
        c.run('coverage html --omit="tests/*"')
        c.run("open htmlcov/index.html")
    else:
        cmd = 'coverage report --sort=cover --show-missing --omit="tests/*"'
        c.run(cmd)


@task(post=[lint])
def black(c):
    "black-format things."
    c.run("python -m black .")


@task(pre=[test, accept, playwright])
def fulltest(c):  # pylint: disable=unused-argument
    """
    Run full tests check.
    """
    print("Done.")


@task(pre=[fulltest, black, lint])
def full(c):  # pylint: disable=unused-argument
    """
    Run full check and lint.
    """
    print("Done.")


ns = Collection()
ns.add_task(fulltest)
ns.add_task(full)
ns.add_task(lint)
ns.add_task(test)
ns.add_task(accept)
ns.add_task(playwright)
ns.add_task(coverage)
ns.add_task(todos)
ns.add_task(start)
ns.add_task(search)
ns.add_task(black)


##############################
# DB tasks


@task(pre=[_ensure_test_db])
def db_wipe(c):
    """
    Wipe the data from the testing db; factory reset settings. :-)

    Can only be run on a testing db.
    """
    c.run("pytest -m dbwipe")
    print("ok")


@task(pre=[_ensure_test_db])
def db_reset(c):
    """
    Reset the database to the demo data.

    Can only be run on a testing db.
    """
    c.run("pytest -m dbdemoload")
    print("ok")


def _schema_dir():
    "Return full path to schema dir."
    thisdir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(thisdir, "lute", "db", "schema")


def _do_schema_export(c, destfile, header_notes, taskname):
    """
    Generate the dumpfile at destfile.
    """
    destfile = os.path.join(_schema_dir(), destfile)
    tempfile = f"{destfile}.temp"
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
    print(f"{destfile} updated (git diff follows):")
    print("DIFF START " + "-" * 38)
    # -U0 = no context before or after changes.
    c.run(f"git diff -U0 -- {destfile}")
    print("DIFF END " + "-" * 40)
    print()


@task
def db_export_baseline(c):
    """
    Reset the db, and create a new baseline db file from the current db.
    """

    # Running the delete task before this one as a pre- step was
    # causing problems (sqlite file not in correct state), so this
    # asks the user to verify.
    text = input("Have you reset the db?  (y/n): ")
    if text != "y":
        print("quitting.")
        return
    _do_schema_export(
        c, "baseline.sql", "Baseline db with demo data.", "db.export.baseline"
    )

    fname = os.path.join(_schema_dir(), "baseline.sql")
    print(f"Verifying {fname}")
    with open(fname, "r", encoding="utf-8") as f:
        checkstring = "Tutorial follow-up"
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
    text = input("Have you **WIPED** the db?  (y/n): ")
    if text != "y":
        print("quitting.")
        return
    _do_schema_export(c, "empty.sql", "EMPTY DB.", "db.export.empty")


@task(help={"suffix": "suffix to add to filename."})
def db_newscript(c, suffix):  # pylint: disable=unused-argument
    """
    Create a new migration, <datetime>_suffix.sql
    """
    now = datetime.now()
    fnow = now.strftime("%Y%m%d")
    filename = f"{fnow}_{suffix}.sql"
    destfile = os.path.join(_schema_dir(), "migrations", filename)
    with open(destfile, "w", encoding="utf-8") as f:
        f.write("-- TODO - fill this in.")
    print("migration created:")
    print(destfile)


dbtasks = Collection("db")
dbtasks.add_task(db_reset, "reset")
dbtasks.add_task(db_wipe, "wipe")
dbtasks.add_task(db_newscript, "newscript")
dbexport = Collection("export")
dbexport.add_task(db_export_baseline, "baseline")
dbexport.add_task(db_export_empty, "empty")
dbtasks.add_collection(dbexport)

ns.add_collection(dbtasks)
