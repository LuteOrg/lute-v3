"""
Common fixtures used by many tests.
"""

import os
import yaml
import pytest

from sqlalchemy import text

from lute.app_config import AppConfig
from lute.db import db
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
    configfile = os.path.join(thisdir, '..', 'config', 'config.yml')

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


@pytest.fixture(name="_demo_db")
def fixture_demo_db(testconfig):
    """
    A clean instance of the demo database.
    """
    if os.path.exists(testconfig.dbfilename):
        os.unlink(testconfig.dbfilename)
    init_db_and_app(testconfig, { 'TESTING': True })


def _delete_all_from_database(app):
    "Clean out all db tables."
        # Clearing everything out in ref-integrity order.
    tables = [
        "sentences",
        "settings",

        "booktags",
        "bookstats",

        "wordtags",
        "wordparents",
        "wordimages",
        "wordflashmessages",

        "tags",
        "tags2",
        "texts",
        "books",
        "words",
        "languages"
    ]
    with app.app_context():
        with db.engine.begin() as conn:
            for t in tables:
                conn.execute(text(f"delete from {t}"))


@pytest.fixture(name="_empty_db")
def fixture_empty_db(testconfig):
    """
    An empty db!
    """
    if os.path.exists(testconfig.dbfilename):
        os.unlink(testconfig.dbfilename)
    app = init_db_and_app(testconfig, { 'TESTING': True })
    _delete_all_from_database(app)
    with app.app_context():
        yield


@pytest.fixture(name="app_with_demo")
def fixture_demo_app(testconfig):
    """
    App with database loaded with demo data.
    """
    if os.path.exists(testconfig.dbfilename):
        os.unlink(testconfig.dbfilename)
    app = init_db_and_app(testconfig, { 'TESTING': True })
    yield app


@pytest.fixture(name = "demo_client")
def fixture_demo_client(app_with_demo):
    """
    Client using demo-data-loaded application.
    """
    return app_with_demo.test_client()


@pytest.fixture(name = "empty_client")
def fixture_empty_client(app_with_demo):
    """
    Client using empty database application.
    """
    _delete_all_from_database(app_with_demo)
    return app_with_demo.test_client()
