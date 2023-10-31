"""
Testing management functions.

"management" is for global actions like clearing out the db.
"""

import pytest
from lute.db import db
from lute.models.setting import Setting
from lute.db.management import delete_all_data
from tests.dbasserts import assert_record_count_equals


@pytest.mark.dbwipe
def test_wiping_db_clears_out_all_tables(app_context):
    """
    DB is wiped clean if requested ... settings are left!

    This test is also used from /tasks.py; see .pytest.ini.
    """
    old_settings = [
        s.key for s in db.session.query(Setting).all()
    ]

    delete_all_data()
    tables = [
        'books',
        'bookstats',
        'booktags',
        'languages',
        'sentences',
        'tags',
        'tags2',
        'texts',
        'wordflashmessages',
        'wordimages',
        'wordparents',
        'words',
        'wordtags'
    ]
    for t in tables:
        assert_record_count_equals(t, 0, t)

    assert_record_count_equals('settings', len(old_settings), 'settings remain')
    sql = 'select * from settings where StValue is null'
    assert_record_count_equals(sql, len(old_settings), 'nulled')


def test_can_get_backup_settings_when_db_is_wiped(app_context):
    "The backupsettings struct assumes certain things about the data."
    delete_all_data()
    bs = Setting.get_backup_settings()
    assert bs.is_acknowledged() is False, 'null = not ackd'
