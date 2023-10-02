"""
Test main entry point.
"""

import os
import sqlite3
from contextlib import closing
import yaml
import pytest

from lute.app_config import AppConfig
from lute.main import init_db_and_app


@pytest.fixture(name="testconfig")
def fixture_config():
    """
    Build app config using config in config/config.yml.

    Special configuration for test runs required:

    DBNAME must start with test_

    DATAPATH must be specified: this ensures that the tests don't
    accidentally write into the user_data (which could mess with prod
    data/media etc)
    """
    thisdir = os.path.dirname(os.path.realpath(__file__))
    configfile = os.path.join(thisdir, '..', '..', 'config', 'config.yml')

    config = None
    with open(configfile, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    failures = []
    if 'DATAPATH' not in config:
        failures.append("add DATAPATH")

    dbname = config.get('DBNAME')
    if not dbname.startswith('test_'):
        failures.append("DBNAME must start with test_")

    if len(failures) > 0:
        msg = f"Bad config.yml: {', '.join(failures)}"
        pytest.exit(msg)

    ac = AppConfig(configfile)
    yield ac


def test_init_no_existing_database(testconfig):
    """
    If no db exists, init should:
    - do the db setup
    - create the flask app
    """
    if os.path.exists(testconfig.dbfilename):
        os.unlink(testconfig.dbfilename)

    app = init_db_and_app()

    assert os.path.exists(testconfig.dbfilename) is True, 'db exists'
    assert testconfig.dbname.startswith('test_')

    def assert_tables_exist(msg: str):
        with closing(sqlite3.connect(testconfig.dbfilename)) as conn:
            cur = conn.cursor()
            sql = """SELECT name FROM sqlite_master
            WHERE type='table' AND name in ('words', 'languages')
            order by name;"""
            tnames = cur.execute(sql).fetchall()
            tnames = [t[0] for t in tnames]
            assert tnames == [ 'languages', 'words' ], msg
    assert_tables_exist('db set up correctly')

    client = app.test_client()
    response = client.get('/')
    assert b'Lute' in response.data
