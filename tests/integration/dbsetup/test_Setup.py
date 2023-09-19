"""
DB setup tests using fake baseline, migration files.
"""

import os
import pytest
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

    d = tmp_path / 'backups'
    d.mkdir()

    thisdir = os.path.dirname(os.path.realpath(__file__))
    baselinedir = os.path.join(thisdir, 'schema', 'baseline')
    migdir = os.path.join(thisdir, 'schema', 'migrations')
    repeatable = os.path.join(thisdir, 'schema', 'repeatable')


    assert os.path.exists(dbfile), 'db was created'

    # todo: check tables exist
    # migrations run
    # no backup
