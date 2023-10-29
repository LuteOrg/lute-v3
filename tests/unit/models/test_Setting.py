"""
Settings test.
"""

from lute.db import db
from lute.models.setting import Setting
from tests.dbasserts import assert_sql_result


def test_save_and_retrieve(app_context):
    "Smoke tests."
    sql = "select StValue from settings where StKey = 'zztrash'"
    assert_sql_result(sql, [], 'not set')
    Setting.set_value('zztrash', 42)
    assert_sql_result(sql, [], 'still not set')

    db.session.commit()
    assert_sql_result(sql, [ '42' ], 'now set')

    v = Setting.get_value('zztrash')
    assert v == '42', 'is string'


def test_missing_value_value_is_nullapp_context(app_context):
    "Missing key = None."
    assert Setting.get_value('missing') is None, 'missing key'


def test_smoke_last_backup(app_context):
    "Check syntax only."
    v = Setting.get_last_backup_datetime()
    assert v is None, 'not set'

    Setting.set_last_backup_datetime(42)
    v = Setting.get_last_backup_datetime()
    assert v == 42, 'set _and_ saved'


def test_get_backup_settings(app_context):
    "Smoke test."
    Setting.set_value('backup_dir', 'blah')
    Setting.set_value('backup_count', 12)
    Setting.set_value('backup_warn', 0)
    db.session.commit()
    b = Setting.get_backup_settings()
    assert isinstance(b, Setting.BackupSettings)
    assert b.backup_dir == 'blah'
    assert b.backup_auto is True  # initial default
    assert b.backup_warn is False
    assert b.backup_count == 12
    assert b.last_backup_datetime is None
