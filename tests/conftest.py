"""
Common fixtures used by many tests.
"""

import os
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
    init_db_and_app(testconfig)
