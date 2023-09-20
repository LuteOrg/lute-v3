"""
DB setup tests using fake baseline, migration files.
"""

import os
import pytest
import sqlite3
from contextlib import closing

from lute.dbsetup.setup import Setup

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

    setup = Setup(dbfile, backups, migrations)
    setup.setup()

    assert os.path.exists(dbfile), 'db was created'

    with closing(sqlite3.connect(dbfile)) as conn:
        cur = conn.cursor()
        sql = """SELECT name FROM sqlite_master
        WHERE type='table' AND name in ('A', 'B')
        order by name;"""
        listOfTables = cur.execute(sql).fetchall()
        assert listOfTables == [ 'A', 'B' ], 'migrations run'

    # assert no backup
