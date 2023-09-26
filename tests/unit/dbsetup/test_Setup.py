"""
DB setup tests using fake baseline, migration files.
"""

import os
import sqlite3
from contextlib import closing
import pytest

from lute.dbsetup.setup import Setup


class MockBackupManager: # pylint: disable=too-few-public-methods
    """
    Fake backup manager to use for tests.
    Can't figure out how to use monkeypatching or
    mocking for objects, so this stub will do
    for now.
    """

    def __init__(self):
        self.backup_called = False

    def handle_backup(self):
        """
        Record if backup was called.
        """
        self.backup_called = True


class MockMigrator: # pylint: disable=too-few-public-methods
    """
    Fake migrator to use for tests.
    """

    def __init__(self):
        self.has_migrations = False
        self.throw_on_migration = False
        self.migrations_run = False

    def do_migration(self, conn): # pylint: disable=unused-argument
        """
        Record if migrations run.
        """
        if self.throw_on_migration:
            raise RuntimeError('some error')
        self.migrations_run = True


@pytest.fixture(name="fakebackupmanager")
def fixture_fakebackupmanager():
    """
    Fake object for tests.
    """
    return MockBackupManager()


@pytest.fixture(name="fakemigrator")
def fixture_fakemigrator():
    """
    Fake object for tests.
    """
    return MockMigrator()


@pytest.fixture(name="baseline")
def baseline_schema(tmp_path):
    """
    Baseline schema file used for setup.
    """
    baseline_file = tmp_path / 'baseline.sql'
    content = "create table A (a int);"
    baseline_file.write_text(content)
    return baseline_file


def test_new_database(baseline, tmp_path, fakebackupmanager, fakemigrator):
    """
    If no db exists, setup should:
    - create the db using the baseline
    - run any migrations
    - no backup created
    """
    dbfile = tmp_path / 'testdb.db'
    assert os.path.exists(dbfile) is False, 'no db exists'

    fakemigrator.has_migrations = True
    setup = Setup(dbfile, baseline, fakebackupmanager, fakemigrator)
    setup.setup()

    assert os.path.exists(dbfile), 'db was created'
    assert fakemigrator.migrations_run, 'migrations were run'
    assert fakebackupmanager.backup_called is False, 'no backup called'


def test_existing_database_new_migrations(tmp_path, fakebackupmanager, fakemigrator):
    """
    If db exists, setup should:
    - run any migrations
    - create a backup, with today's datetime
    - should only keep the last X migrations
    """
    dbfile = tmp_path / 'testdb.db'
    assert os.path.exists(dbfile) is False, 'no db exists'

    thisdir = os.path.dirname(os.path.realpath(__file__))
    baseline = os.path.join(thisdir, 'schema', 'baseline', 'schema.sql')
    with open(baseline, 'r', encoding='utf8') as f:
        sql = f.read()
    with closing(sqlite3.connect(dbfile)) as conn:
        conn.executescript(sql)

    fakemigrator.has_migrations = True
    setup = Setup(dbfile, baseline, fakebackupmanager, fakemigrator)
    setup.setup()

    assert os.path.exists(dbfile), 'db was created'
    assert fakemigrator.migrations_run, 'migrations were run'
    assert fakebackupmanager.backup_called, 'backup was called'


def test_existing_database_no_new_migrations(tmp_path, fakebackupmanager, fakemigrator):
    """
    DB should be left as-is, no migrations run, no backup.
    """
    dbfile = tmp_path / 'testdb.db'
    assert os.path.exists(dbfile) is False, 'no db exists'

    thisdir = os.path.dirname(os.path.realpath(__file__))
    baseline = os.path.join(thisdir, 'schema', 'baseline', 'schema.sql')
    with open(baseline, 'r', encoding='utf8') as f:
        sql = f.read()
    with closing(sqlite3.connect(dbfile)) as conn:
        conn.executescript(sql)

    fakemigrator.has_migrations = False
    setup = Setup(dbfile, baseline, fakebackupmanager, fakemigrator)
    setup.setup()

    assert os.path.exists(dbfile), 'db was created'
    assert fakemigrator.migrations_run is False, 'no migrations were run'
    assert fakebackupmanager.backup_called is False, 'no backup was called'


# Tests to write:
# BackupManager tests:
# - backup created
# - max number of files remain
