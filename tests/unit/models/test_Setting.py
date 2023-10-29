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
    Setting.set_key('zztrash', 42)
    assert_sql_result(sql, [], 'still not set')

    db.session.commit()
    assert_sql_result(sql, [ '42' ], 'now set')

    v = Setting.get_key('zztrash')
    assert v == '42', 'is string'


def test_missing_key_value_is_nullapp_context(app_context):
    "Missing key = None."
    assert Setting.get_key('missing') is None, 'missing key'


def test_smoke_last_backup(app_context):
    "Check syntax only."
    v = Setting.get_last_backup_datetime()
    assert v is None, 'not set'

    Setting.set_last_backup_datetime(42)
    v = Setting.get_last_backup_datetime()
    assert v == 42, 'set _and_ saved'
