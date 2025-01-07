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
import threading
import time
from datetime import datetime
import requests
from invoke import task, Collection
from lute.config.app_config import AppConfig

# pylint: disable=unused-argument


@task
def lint(c):
    "Run pylint on lute/ and tests/."
    print("Starting lint")
    # Formats: https://pylint.pycqa.org/en/latest/user_guide/usage/output.html
    msgfmt = [
        "--ignore-patterns='zz_.*.py'",
        "--msg-template='{path} ({line:03d}): {msg} ({msg_id} {symbol})'",
    ]
    c.run(f"pylint {' '.join(msgfmt)} tasks.py lute/ tests/")


@task
def lint_changed(c):
    "Run pylint on changed files only.  (*nix machines only)"
    c.run("for p in `git diff --name-only | grep py`; do echo $p; pylint $p; done")


@task
def todos(c):
    """
    Print code TODOs.
    """
    c.run("python utils/todos.py")


@task(help={"port": "optional port to run on; default = 5001"})
def start(c, port=5001):
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
    "Return True if running on port."
    try:
        resp = requests.get(f"http://localhost:{useport}", timeout=5)
        if resp.status_code != 200:
            raise RuntimeError(f"Got code {resp.status_code} ... ???")
        return True
    except requests.exceptions.ConnectionError:
        return False


def _wait_for_running_site(port):
    "Wait until the site is running."
    url = f"http://localhost:{port}"
    is_running = False
    attempt_count = 0
    print(f"Wait until site is running at {url} ...", flush=True)
    while attempt_count < 10 and not is_running:
        attempt_count += 1
        try:
            # print(f"  Attempt {attempt_count}", flush=True)
            requests.get(url, timeout=5)
            print(f"Site is running (succeeded on attempt {attempt_count})", flush=True)
            is_running = True
        except requests.exceptions.ConnectionError:
            time.sleep(1)
    if not is_running:
        raise Exception("Site didn't start?")  # pylint: disable=broad-exception-raised


def _run_browser_tests(port, run_test):
    "Start server on port, and run tests."
    tests_failed = False
    if _site_is_running(port):
        raise RuntimeError(f"Site already running on port {port}, quitting")

    def print_subproc_output(pipe, label):
        """Prints output from a given pipe with a label."""
        for line in iter(pipe.readline, b""):
            print(f"[{label}] {line.decode().strip()}", flush=True)
        pipe.close()

    cmd = ["python", "-m", "tests.acceptance.start_acceptance_app", f"{port}"]
    with subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    ) as app_process:
        _wait_for_running_site(port)
        stdout_thread = threading.Thread(
            target=print_subproc_output, args=(app_process.stdout, "STDOUT")
        )
        stderr_thread = threading.Thread(
            target=print_subproc_output, args=(app_process.stderr, "STDERR")
        )
        stdout_thread.start()
        stderr_thread.start()
        try:
            subprocess.run(run_test, check=True)
        except subprocess.CalledProcessError:
            # This just means a test failed.  We don't need to see
            # a stack trace, the assert failures are already displayed.
            tests_failed = True
        finally:
            app_process.terminate()
            stdout_thread.join()
            stderr_thread.join()

    if tests_failed:
        raise RuntimeError("tests failed")


def _run_acceptance(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    c,
    port=5001,
    show=False,
    noheadless=False,
    kflag=None,
    mobile=False,
    exitfirst=False,
    verbose=False,
):
    """
    Start lute, run tests/acceptance tests, screenshot fails.

    If no port specified, use default 5001.

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
    if mobile:
        run_test.append("-m mobile")
        run_test.append("--mobile")

    _run_browser_tests(5001, run_test)


acceptance_help = {
    "port": "optional port to run on; creates server if needed.",
    "show": "print data",
    "noheadless": "run as non-headless (default is headless, i.e. not shown)",
    "kflag": "optional -k flag argument",
    "exitfirst": "exit on first failure",
    "verbose": "make verbose",
}


@task(
    pre=[_ensure_test_db],
    help=acceptance_help,
)
def accept(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    c,
    port=5001,
    show=False,
    noheadless=False,
    kflag=None,
    exitfirst=False,
    verbose=False,
):
    "Run acceptance tests, full browser."
    _run_acceptance(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        c,
        port=port,
        show=show,
        noheadless=noheadless,
        kflag=kflag,
        mobile=False,
        exitfirst=exitfirst,
        verbose=verbose,
    )


@task(
    pre=[_ensure_test_db],
    help=acceptance_help,
)
def acceptmobile(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    c,
    port=5001,
    show=False,
    noheadless=False,
    kflag=None,
    exitfirst=False,
    verbose=False,
):
    "Run acceptance tests, mobile emulation, tests marked @mobile."
    _run_acceptance(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        c,
        port=port,
        show=show,
        noheadless=noheadless,
        kflag=kflag,
        mobile=True,
        exitfirst=exitfirst,
        verbose=verbose,
    )


@task(pre=[_ensure_test_db])
def playwright(c):
    """
    Start lute, run playwright tests.  export SHOW=true env var to run non-headless.

    Only uses port 5001.

    If Lute's not running on specified port, start a server.
    """
    run_test = ["pytest", "tests/playwright/playwright.py", "-s"]
    _run_browser_tests(5001, run_test)


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


@task
def black(c):
    "black-format things."
    c.run("python -m black .")


@task(pre=[test, accept, acceptmobile, playwright])
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
ns.add_task(lint_changed)
ns.add_task(test)
ns.add_task(accept)
ns.add_task(acceptmobile)
ns.add_task(playwright)
ns.add_task(coverage)
ns.add_task(todos)
ns.add_task(start)
ns.add_task(search)
ns.add_task(black)


##############################
# DB tasks


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
    Create a new baseline db file from the current db.
    """
    _do_schema_export(
        c,
        "baseline.sql",
        "Baseline db with flag to load demo data.",
        "db.export.baseline",
    )

    fname = os.path.join(_schema_dir(), "baseline.sql")
    print(f"Verifying {fname}")
    with open(fname, "r", encoding="utf-8") as f:
        checkstring = 'CREATE TABLE IF NOT EXISTS "languages"'
        if checkstring in f.read():
            print(f'"{checkstring}" found, likely ok.')
        else:
            print(f'"{checkstring}" NOT FOUND, SOMETHING LIKELY WRONG.')
            raise RuntimeError(f'Missing "{checkstring}" in exported file.')


@task(pre=[_ensure_test_db])
def db_reset(c):
    """
    Reset the database to baseline state for new installations, with LoadDemoData system flag set.

    Can only be run on a testing db.
    """
    c.run("pytest -m dbreset")
    print("\nok, export baseline.sql if needed.\n")


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
dbtasks.add_task(db_newscript, "newscript")
dbexport = Collection("export")
dbexport.add_task(db_export_baseline, "baseline")
dbtasks.add_collection(dbexport)

ns.add_collection(dbtasks)
