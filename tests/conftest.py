"""
Common fixtures used by many tests.
"""

import os
import yaml
import pytest

from lute.config.app_config import AppConfig
from lute.db import db
import lute.db.demo
from lute.app_factory import create_app

from lute.models.language import Language


def pytest_sessionstart(session):  # pylint: disable=unused-argument
    """
    Ensure test config defines a test environment.

    Special configuration for test runs required:

    DBNAME must start with test_

    DATAPATH must be specified: this ensures that the tests don't
    accidentally write into the user_data (which could mess with prod
    data/media etc)
    """
    thisdir = os.path.dirname(os.path.realpath(__file__))
    configfile = os.path.join(thisdir, "..", "lute", "config", "config.yml")

    config = None
    with open(configfile, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    failures = []
    if "DATAPATH" not in config:
        failures.append("DATAPATH not in config file")

    ac = AppConfig(configfile)

    if not ac.is_test_db:
        failures.append("DBNAME in config.yml must start with test_")
    if len(failures) > 0:
        msg = f"Bad config.yml: {', '.join(failures)}"
        pytest.exit(msg)


@pytest.fixture(name="testconfig")
def fixture_config():
    "Config using the app config."
    ac = AppConfig(AppConfig.default_config_filename())
    yield ac


@pytest.fixture(name="app")
def fixture_app():
    """
    A clean instance of the demo database.

    I'm not a _huge_ fan of this because if the app
    is open while tests are running, the app seems to hold
    on to references to the old deleted db ...
    that said, it's much faster to do this than to do a
    "wipe and reload database" on every test run.
    """
    config_file = AppConfig.default_config_filename()
    c = AppConfig(config_file)
    if os.path.exists(c.dbfilename):
        os.unlink(c.dbfilename)
    extra_config = {"WTF_CSRF_ENABLED": False, "TESTING": True}
    app = create_app(config_file, extra_config=extra_config)
    yield app


@pytest.fixture(name="app_context")
def fixture_app_context(app):
    """
    Yields the app context so that tests using the db will work.
    """
    with app.app_context():
        yield


@pytest.fixture(name="empty_db")
def fixture_empty_db(app_context):
    """
    Wipe the db.
    """
    lute.db.management.delete_all_data()


@pytest.fixture(name="client")
def fixture_demo_client(app):
    """
    Client using demo-data-loaded application.
    """
    return app.test_client()


@pytest.fixture(name="demo_yaml_folder")
def fixture_yaml_folder():
    "Path to the demo files."
    return os.path.join(lute.db.demo.demo_data_path(), "languages")


def _get_language(f):
    """
    Return language from the db if it already exists,
    or create it from the file.
    """
    lang = lute.db.demo.get_demo_language(f)
    db_language = db.session.query(Language).filter(Language.name == lang.name).first()
    if db_language is None:
        return lang
    return db_language


@pytest.fixture(name="test_languages")
def fixture_test_languages(app_context, demo_yaml_folder):
    "Dict of available languages for tests."
    # Hardcoded = good enough.
    langs = ["spanish", "english", "japanese", "turkish", "classical_chinese"]
    ret = {}
    for lang in langs:
        f = os.path.join(demo_yaml_folder, f"{lang}.yaml")
        ret[lang] = _get_language(f)
    yield ret


@pytest.fixture(name="spanish")
def fixture_spanish(test_languages):
    return test_languages["spanish"]


@pytest.fixture(name="english")
def fixture_english(test_languages):
    return test_languages["english"]


@pytest.fixture(name="japanese")
def fixture_japanese(test_languages):
    return test_languages["japanese"]


@pytest.fixture(name="turkish")
def fixture_turkish(test_languages):
    return test_languages["turkish"]


@pytest.fixture(name="classical_chinese")
def fixture_cl_chinese(test_languages):
    return test_languages["classical_chinese"]
