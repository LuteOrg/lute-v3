"""
DB setup tests using fake baseline, migration files.
"""

import os
import gzip
import sqlite3
from contextlib import closing
import pytest

from lute.db.setup.main import Setup, BackupManager
from lute.db.setup.migrator import SqliteMigrator


class MockBackupManager:  # pylint: disable=too-few-public-methods
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


class MockMigrator:  # pylint: disable=too-few-public-methods
    """
    Fake migrator to use for tests.
    """

    def __init__(self):
        self.has_pending_migrations = False
        self.migrations_run = False

    def has_migrations(self, conn):  # pylint: disable=unused-argument
        """
        Refs self.has_pending_migrations.
        """
        return self.has_pending_migrations

    def do_migration(self, conn):  # pylint: disable=unused-argument
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
    baseline_file = tmp_path / "baseline.sql"
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
    dbfile = tmp_path / "testdb.db"
    assert os.path.exists(dbfile) is False, "no db exists"

    fakemigrator.has_pending_migrations = True
    setup = Setup(dbfile, baseline, fakebackupmanager, fakemigrator)
    setup.setup()

    assert os.path.exists(dbfile), "db was created"
    assert fakemigrator.migrations_run, "migrations were run"
    assert fakebackupmanager.backup_called is False, "no backup called"


def test_existing_database_new_migrations(
    baseline, tmp_path, fakebackupmanager, fakemigrator
):
    """
    If db exists, setup should:
    - run any migrations
    - create a backup
    """
    dbfile = tmp_path / "testdb.db"
    dbfile.write_text("content")
    assert os.path.exists(dbfile), "db exists"

    fakemigrator.has_pending_migrations = True
    setup = Setup(dbfile, baseline, fakebackupmanager, fakemigrator)
    setup.setup()

    assert os.path.exists(dbfile), "db still there"
    assert fakemigrator.migrations_run, "migrations were run"
    assert fakebackupmanager.backup_called, "backup was called"


def test_existing_db_no_migrations(baseline, tmp_path, fakebackupmanager, fakemigrator):
    """
    DB should be left as-is, no migrations run, and *no* backup created.
    """
    dbfile = tmp_path / "testdb.db"
    dbfile.write_text("content")
    assert os.path.exists(dbfile), "db exists"

    fakemigrator.has_pending_migrations = False
    setup = Setup(dbfile, baseline, fakebackupmanager, fakemigrator)
    setup.setup()

    assert os.path.exists(dbfile), "db still there"
    assert fakemigrator.migrations_run, "migrations were run"
    assert fakebackupmanager.backup_called is False, "NO backup was called"


@pytest.fixture(name="migrator")
def fixture_migrator():
    """
    Migrator using the migration files in ./schema.
    """
    thisdir = os.path.dirname(os.path.realpath(__file__))
    migdir = os.path.join(thisdir, "schema", "migrations")
    repeatable = os.path.join(thisdir, "schema", "repeatable")
    return SqliteMigrator(migdir, repeatable)


def test_happy_path_no_existing_database(tmp_path, migrator):
    """
    If no db exists, setup should:
    - create the db using the baseline
    - run any migrations
    - no backup created
    """

    dbfile = tmp_path / "testdb.db"
    assert os.path.exists(dbfile) is False, "no db exists"

    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()

    thisdir = os.path.dirname(os.path.realpath(__file__))
    baseline = os.path.join(thisdir, "schema", "baseline", "schema.sql")

    bm = BackupManager(dbfile, backup_dir, 3)

    setup = Setup(dbfile, baseline, bm, migrator)
    setup.setup()

    assert os.path.exists(dbfile), "db was created"

    with closing(sqlite3.connect(dbfile)) as conn:
        cur = conn.cursor()
        sql = """SELECT name FROM sqlite_master
        WHERE type='table' AND name in ('A', 'B')
        order by name;"""
        tnames = cur.execute(sql).fetchall()
        tnames = [t[0] for t in tnames]
        assert tnames == ["A", "B"], "migrations run"

    backup_files = list(backup_dir.glob("*.gz"))
    assert len(backup_files) == 0, "no backups"


def test_existing_database_with_migrations(tmp_path, migrator):
    """
    If db exists, setup should:
    - run any migrations
    - create a backup with today's datetime
    """

    dbfile = tmp_path / "testdb.db"
    assert os.path.exists(dbfile) is False, "no db exists"

    thisdir = os.path.dirname(os.path.realpath(__file__))
    baseline = os.path.join(thisdir, "schema", "baseline", "schema.sql")
    with open(baseline, "r", encoding="utf8") as f:
        with closing(sqlite3.connect(dbfile)) as conn:
            conn.executescript(f.read())
    assert os.path.exists(dbfile) is True, "db exists"

    def assert_tables(expected: list, msg: str):
        with closing(sqlite3.connect(dbfile)) as conn:
            cur = conn.cursor()
            sql = """SELECT name FROM sqlite_master
            WHERE type='table' AND name in ('A', 'B')
            order by name;"""
            tnames = cur.execute(sql).fetchall()
            tnames = [t[0] for t in tnames]
            assert tnames == expected, msg

    assert_tables(["A"], "initial state")

    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()

    bm = BackupManager(dbfile, backup_dir, 3)

    setup = Setup(dbfile, baseline, bm, migrator)
    setup.setup()

    assert os.path.exists(dbfile), "db still exists"
    assert_tables(["A", "B"], "migrations run")

    backup_files = list(backup_dir.glob("*.gz"))
    print(backup_files)
    assert len(backup_files) == 1, "backup created"

    # Restore backup
    with gzip.open(backup_files[0], "rb") as gzipped_file, open(
        dbfile, "wb"
    ) as output_file:
        data = gzipped_file.read()
        output_file.write(data)

    assert_tables(["A"], "back to initial state")


def test_existing_database_no_outstanding_migrations(tmp_path, migrator):
    """
    If db exists and no migrations are outstand, setup should:
    - not run any migrations
    - NOT create a backup
    """

    dbfile = tmp_path / "testdb.db"
    assert os.path.exists(dbfile) is False, "no db exists"

    thisdir = os.path.dirname(os.path.realpath(__file__))
    baseline = os.path.join(thisdir, "schema", "baseline", "schema.sql")
    with open(baseline, "r", encoding="utf8") as f:
        with closing(sqlite3.connect(dbfile)) as conn:
            conn.executescript(f.read())
    assert os.path.exists(dbfile) is True, "db exists"

    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    bm = BackupManager(dbfile, backup_dir, 3)

    setup = Setup(dbfile, baseline, bm, migrator)
    setup.setup()

    assert os.path.exists(dbfile), "db still exists"

    backup_files = list(backup_dir.glob("*.gz"))
    assert len(backup_files) == 1, "backup created"

    # Clean state before next run.
    for f in backup_files:
        os.unlink(f)
    backup_files = list(backup_dir.glob("*.gz"))
    assert len(backup_files) == 0, "no backups"

    setup.setup()
    backup_files = list(backup_dir.glob("*.gz"))
    assert len(backup_files) == 0, "STILL no backups"
