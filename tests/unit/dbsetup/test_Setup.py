"""
DB setup tests using fake baseline, migration files.
"""

import os
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

    def do_backup(self):
        """
        Record if backup was called.
        """
        self.backup_called = True


class MockMigrator: # pylint: disable=too-few-public-methods
    """
    Fake migrator to use for tests.
    """

    def __init__(self):
        self.has_pending_migrations = False
        self.migrations_run = False

    def has_migrations(self, conn): # pylint: disable=unused-argument
        """
        Refs self.has_pending_migrations.
        """
        return self.has_pending_migrations

    def do_migration(self, conn): # pylint: disable=unused-argument
        """
        Record if migrations run.
        """
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

    fakemigrator.has_pending_migrations = True
    setup = Setup(dbfile, baseline, fakebackupmanager, fakemigrator)
    setup.setup()

    assert os.path.exists(dbfile), 'db was created'
    assert fakemigrator.migrations_run, 'migrations were run'
    assert fakebackupmanager.backup_called is False, 'no backup called'


def test_existing_database_new_migrations(baseline, tmp_path, fakebackupmanager, fakemigrator):
    """
    If db exists, setup should:
    - run any migrations
    - create a backup
    """
    dbfile = tmp_path / 'testdb.db'
    dbfile.write_text('content')
    assert os.path.exists(dbfile), 'db exists'

    fakemigrator.has_pending_migrations = True
    setup = Setup(dbfile, baseline, fakebackupmanager, fakemigrator)
    setup.setup()

    assert os.path.exists(dbfile), 'db still there'
    assert fakemigrator.migrations_run, 'migrations were run'
    assert fakebackupmanager.backup_called, 'backup was called'


def test_existing_db_no_migrations(baseline, tmp_path, fakebackupmanager, fakemigrator):
    """
    DB should be left as-is, no migrations run, backup created.
    """
    dbfile = tmp_path / 'testdb.db'
    dbfile.write_text('content')
    assert os.path.exists(dbfile), 'db exists'

    fakemigrator.has_pending_migrations = False
    setup = Setup(dbfile, baseline, fakebackupmanager, fakemigrator)
    setup.setup()

    assert os.path.exists(dbfile), 'db still there'
    assert fakemigrator.migrations_run, 'migrations were run'
    assert fakebackupmanager.backup_called, 'backup was called'
