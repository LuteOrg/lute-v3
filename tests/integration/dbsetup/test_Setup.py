"""
DB setup tests using fake baseline, migration files.
"""

import os
import sqlite3
from contextlib import closing
import pytest

from lute.dbsetup.setup import Setup, BackupManager
from lute.dbsetup.migrator import SqliteMigrator


@pytest.fixture(name="migrator")
def fixture_migrator():
    """
    Migrator using the migration files in ./schema.
    """
    thisdir = os.path.dirname(os.path.realpath(__file__))
    migdir = os.path.join(thisdir, 'schema', 'migrations')
    repeatable = os.path.join(thisdir, 'schema', 'repeatable')
    return SqliteMigrator(migdir, repeatable)


def test_happy_path_no_existing_database(tmp_path, migrator):
    """
    If no db exists, setup should:
    - create the db using the baseline
    - run any migrations
    - no backup created
    """

    dbfile = tmp_path / 'testdb.db'
    assert os.path.exists(dbfile) is False, 'no db exists'

    backup_dir = tmp_path / 'backups'
    backup_dir.mkdir()

    thisdir = os.path.dirname(os.path.realpath(__file__))
    baseline = os.path.join(thisdir, 'schema', 'baseline', 'schema.sql')

    bm = BackupManager(dbfile, backup_dir, 3)

    setup = Setup(dbfile, baseline, bm, migrator)
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

    backup_files = list(backup_dir.glob('*.gz'))
    assert len(backup_files) == 0, 'no backups'


def test_existing_database(tmp_path, migrator):
    """
    If db exists, setup should:
    - run any migrations
    - create a backup, with today's datetime
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

    backup_dir = tmp_path / 'backups'
    backup_dir.mkdir()

    bm = BackupManager(dbfile, backup_dir, 3)

    setup = Setup(dbfile, baseline, bm, migrator)
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

    backup_files = list(backup_dir.glob('*.gz'))
    print(backup_files)
    assert len(backup_files) == 1, 'backup created'
