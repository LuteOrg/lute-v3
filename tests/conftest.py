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

from lute.models.language import Language

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


@pytest.fixture(name="app")
def fixture_app(testconfig):
    """
    A clean instance of the demo database.
    """
    if os.path.exists(testconfig.dbfilename):
        os.unlink(testconfig.dbfilename)
    extra_config = {
        'WTF_CSRF_ENABLED': False,
        'TESTING': True
    }
    app = init_db_and_app(testconfig, extra_config)
    yield app


@pytest.fixture(name="app_context")
def fixture_app_context(app):
    """
    Yields the app context so that tests using the db will work.
    """
    with app.app_context():
        yield


def _delete_all_from_database():
    "Clean out all db tables.  Requires an app_context to be active."
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
    with db.engine.begin() as conn:
        for t in tables:
            conn.execute(text(f"delete from {t}"))


@pytest.fixture(name="empty_db")
def fixture_empty_db(app_context):
    """
    An empty db!
    """
    _delete_all_from_database()


@pytest.fixture(name = "demo_client")
def fixture_demo_client(app):
    """
    Client using demo-data-loaded application.
    """
    return app.test_client()


@pytest.fixture(name = "empty_client")
def fixture_empty_client(app):
    """
    Client using empty database application.
    """
    with app.app_context():
        _delete_all_from_database()
    return app.test_client()


@pytest.fixture(name="demo_yaml_folder")
def fixture_yaml_folder():
    "Path to the demo files."
    lang_path = "../demo/languages/"
    absolute_path = os.path.abspath(os.path.join(os.path.dirname(__file__), lang_path))
    return absolute_path


@pytest.fixture(name="spanish")
def fixture_spanish(demo_yaml_folder):
    "Make spanish from demo file."
    f = os.path.join(demo_yaml_folder, 'spanish.yaml')
    return Language.from_yaml(f)


@pytest.fixture(name="english")
def fixture_english(demo_yaml_folder):
    "Make spanish from demo file."
    f = os.path.join(demo_yaml_folder, 'english.yaml')
    return Language.from_yaml(f)
