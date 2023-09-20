"""
DB setup tests using fake baseline, migration files.
"""

import os
import pytest
import sqlite3
from contextlib import closing

from lute.dbsetup.setup import Setup, BackupManager

def test_happy_path_no_existing_database(tmp_path):
    """
    If no db exists, setup should:
    - create the db using the baseline
    - run any migrations
    - no backup created
    """

    dbfile = tmp_path / 'testdb.db'
    assert os.path.exists(dbfile) == False, 'no db exists'

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

    bm = BackupManager(dbfile, backups, 'nextfile.db.gz', 5)

    setup = Setup(dbfile, bm, migrations)
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

    assert list(backups.glob('*.gz')) == [], 'no backups'


def test_existing_database_new_migrations(tmp_path):
    """
    If db exists, setup should:
    - run any migrations
    - create a backup, with today's datetime
    - should only keep the last X migrations
    """

    dbfile = tmp_path / 'testdb.db'
    assert os.path.exists(dbfile) == False, 'no db exists'

    thisdir = os.path.dirname(os.path.realpath(__file__))
    baseline = os.path.join(thisdir, 'schema', 'baseline', 'schema.sql')
    with open(baseline, 'r', encoding='utf8') as f:
        sql = f.read()
    with closing(sqlite3.connect(dbfile)) as conn:
        conn.executescript(sql)
    assert os.path.exists(dbfile) == True, 'db exists'

    backups = tmp_path / 'backups'
    backups.mkdir()

    migdir = os.path.join(thisdir, 'schema', 'migrations')
    repeatable = os.path.join(thisdir, 'schema', 'repeatable')
    migrations = {
        'baseline': baseline,
        'migrations': migdir,
        'repeatable': repeatable
    }

    class FakeBackupManager:
        def __init__(self):
            self.backup_called = False
        def handle_backup(self):
            self.backup_called = True

    fbm = FakeBackupManager()
    setup = Setup(dbfile, fbm, migrations)
    setup.setup()

    assert os.path.exists(dbfile), 'db was created'

    assert fbm.backup_called, 'backup was called'

    with closing(sqlite3.connect(dbfile)) as conn:
        cur = conn.cursor()
        sql = """SELECT name FROM sqlite_master
        WHERE type='table' AND name in ('A', 'B')
        order by name;"""
        tnames = cur.execute(sql).fetchall()
        tnames = [t[0] for t in tnames]
        assert tnames == [ 'A', 'B' ], 'migrations run'


def test_existing_database_no_new_migrations(tmp_path):
    """
    DB should be left as-is, no migrations run, no backup.
    """

# TODO:
# BackupManager tests:
# - backup created
# - max number of files remain
