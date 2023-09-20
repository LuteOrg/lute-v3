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


@pytest.fixture(name="fakebackupmanager")
def fixture_fakebackupmanager():
    """
    Fake object for tests.
    """
    return MockBackupManager()



def test_happy_path_no_existing_database(tmp_path, fakebackupmanager):
    """
    If no db exists, setup should:
    - create the db using the baseline
    - run any migrations
    - no backup created
    """

    dbfile = tmp_path / 'testdb.db'
    assert os.path.exists(dbfile) is False, 'no db exists'

    backups = tmp_path / 'backups'
    backups.mkdir()

    thisdir = os.path.dirname(os.path.realpath(__file__))

    baseline = os.path.join(thisdir, 'schema', 'baseline', 'schema.sql')
    migdir = os.path.join(thisdir, 'schema', 'migrations')
    repeatable = os.path.join(thisdir, 'schema', 'repeatable')
    migrations = {
        'baseline': baseline,
        'migrations': migdir,
        'repeatable': repeatable
    }

    setup = Setup(dbfile, fakebackupmanager, migrations)
    setup.setup()

    assert os.path.exists(dbfile), 'db was created'

    with closing(sqlite3.connect(dbfile)) as conn:
        cur = conn.cursor()
        sql = """SELECT name FROM sqlite_master
        WHERE type='table' AND name in ('A', 'B')
        order by name;"""
        tnames = cur.execute(sql).fetchall()
        tnames = [t[0] for t in tnames]
        assert tnames == [ 'A', 'B' ], 'migrations run'

    assert fakebackupmanager.backup_called is False, 'no backup called'


def test_existing_database_new_migrations(tmp_path, fakebackupmanager):
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
    assert os.path.exists(dbfile) is True, 'db exists'

    backups = tmp_path / 'backups'
    backups.mkdir()

    migdir = os.path.join(thisdir, 'schema', 'migrations')
    repeatable = os.path.join(thisdir, 'schema', 'repeatable')
    migrations = {
        'baseline': baseline,
        'migrations': migdir,
        'repeatable': repeatable
    }

    setup = Setup(dbfile, fakebackupmanager, migrations)
    setup.setup()

    assert os.path.exists(dbfile), 'db was created'

    assert fakebackupmanager.backup_called, 'backup was called'

    with closing(sqlite3.connect(dbfile)) as conn:
        cur = conn.cursor()
        sql = """SELECT name FROM sqlite_master
        WHERE type='table' AND name in ('A', 'B')
        order by name;"""
        tnames = cur.execute(sql).fetchall()
        tnames = [t[0] for t in tnames]
        assert tnames == [ 'A', 'B' ], 'migrations run'


def test_existing_database_no_new_migrations():
    """
    DB should be left as-is, no migrations run, no backup.
    """
    a = 1
    assert a == 2, 'to do'


# Tests to write:
# BackupManager tests:
# - backup created
# - max number of files remain
