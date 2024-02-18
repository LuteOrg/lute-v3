"""
Settings test.
"""

import os
from unittest.mock import patch
import pytest
from sqlalchemy import text
from lute.db import db
from lute.models.setting import (
    UserSetting,
    MissingUserSettingKeyException,
    SystemSetting,
    BackupSettings,
)
from tests.dbasserts import assert_sql_result


def test_user_and_system_settings_do_not_intersect(app_context):
    "A UserSetting is not available as a system setting."
    UserSetting.set_value("backup_count", 42)
    db.session.commit()
    sql = "select StValue, StKeyType from settings where StKey = 'backup_count'"
    assert_sql_result(sql, ["42; user"], "loaded")
    u = UserSetting.get_value("backup_count")
    assert u == "42", "found user setting"
    assert SystemSetting.get_value("backup_count") is None, "not in system settings"


def test_save_and_retrieve_user_setting(app_context):
    "Smoke tests."
    UserSetting.set_value("backup_count", 42)
    sql = "select StValue from settings where StKey = 'backup_count'"
    assert_sql_result(sql, ["5"], "still default")

    db.session.commit()
    assert_sql_result(sql, ["42"], "now set")

    v = UserSetting.get_value("backup_count")
    assert v == "42", "is string"


def test_missing_value_value_is_nullapp_context(app_context):
    "Missing key = None."
    assert SystemSetting.get_value("missing") is None, "missing key"


def test_smoke_last_backup(app_context):
    "Check syntax only."
    v = SystemSetting.get_last_backup_datetime()
    assert v is None, "not set"

    SystemSetting.set_last_backup_datetime(42)
    v = SystemSetting.get_last_backup_datetime()
    assert v == 42, "set _and_ saved"


def test_get_backup_settings(app_context):
    "Smoke test."
    UserSetting.set_value("backup_dir", "blah")
    UserSetting.set_value("backup_count", 12)
    UserSetting.set_value("backup_warn", 0)
    db.session.commit()
    b = BackupSettings.get_backup_settings()
    assert b.backup_dir == "blah"
    assert b.backup_auto is True  # initial defaults
    assert b.backup_warn is False  # set to 0 above
    assert b.backup_count == 12
    assert b.last_backup_datetime is None


def test_time_since_last_backup_future(app_context):
    """
    Check formatting when last backup is reported to be in the future.

    current time = 600, backup time = 900
    """
    b = BackupSettings.get_backup_settings()
    with patch("time.time", return_value=600):
        b.last_backup_datetime = 900
        assert b.time_since_last_backup is None


def test_time_since_last_backup_none(app_context):
    """
    Check formatting when last backup is reported to be None.

    current time = 600, backup time = None
    """
    b = BackupSettings.get_backup_settings()
    with patch("time.time", return_value=600):
        b.last_backup_datetime = None
        assert b.time_since_last_backup is None


def test_time_since_last_backup_right_now(app_context):
    """
    Check formatting when last backup is reported to be the same as current time.

    current time = 600, backup time = 600
    """
    b = BackupSettings.get_backup_settings()
    with patch("time.time", return_value=600):
        b.last_backup_datetime = 600
        assert b.time_since_last_backup == "0 seconds ago"


def test_time_since_last_backup_in_past(app_context):
    """
    Check formatting when last backup is reported to be in the past.

    current time = 62899200, backup time = various
    """
    b = BackupSettings.get_backup_settings()
    now = 62899200
    with patch("time.time", return_value=now):
        b.last_backup_datetime = now - 45
        assert b.time_since_last_backup == "45 seconds ago"
        b.last_backup_datetime = now - 75
        assert b.time_since_last_backup == "1 minute ago"
        b.last_backup_datetime = now - 135
        assert b.time_since_last_backup == "2 minutes ago"
        b.last_backup_datetime = now - 3601
        assert b.time_since_last_backup == "1 hour ago"
        b.last_backup_datetime = now - 7201
        assert b.time_since_last_backup == "2 hours ago"
        b.last_backup_datetime = now - 86401
        assert b.time_since_last_backup == "1 day ago"
        b.last_backup_datetime = now - 172801
        assert b.time_since_last_backup == "2 days ago"
        b.last_backup_datetime = now - 604801
        assert b.time_since_last_backup == "1 week ago"
        b.last_backup_datetime = now - 15724801
        assert b.time_since_last_backup == "26 weeks ago"
        b.last_backup_datetime = now - 45360001
        assert b.time_since_last_backup == "75 weeks ago"


def test_user_settings_loaded_with_defaults(app_context):
    "Called on load."
    db.session.execute(text("delete from settings"))
    db.session.commit()
    assert UserSetting.key_exists("backup_dir") is False, "key removed"
    UserSetting.load()
    assert UserSetting.key_exists("backup_dir") is True, "key created"

    # Check defaults
    b = BackupSettings.get_backup_settings()
    assert b.backup_enabled is True
    assert b.backup_dir is not None
    assert b.backup_auto is True
    assert b.backup_warn is True
    assert b.backup_count == 5


def test_user_settings_load_leaves_existing_values(app_context):
    "Called on load."
    UserSetting.set_value("backup_count", 17)
    db.session.commit()
    assert UserSetting.get_value("backup_count") == "17"
    UserSetting.load()
    b = BackupSettings.get_backup_settings()
    assert b.backup_count == 17, "still 17"


def test_get_or_set_user_setting_unknown_key_throws(app_context):
    "Safety, ensure no typo for user settings."
    with pytest.raises(MissingUserSettingKeyException):
        UserSetting.get_value("bad_key")
    with pytest.raises(MissingUserSettingKeyException):
        UserSetting.set_value("bad_key", 17)


def test_setting_mecab_path_sets_env_var(app_context):
    "Natto-py needs an env var."
    UserSetting.set_value("mecab_path", "blah")
    assert os.environ["MECAB_PATH"] == "blah", "was set"
    UserSetting.set_value("mecab_path", None)
    assert os.environ.get("MECAB_PATH", "X") == "X", "not set"
    UserSetting.set_value("mecab_path", "")
    assert os.environ.get("MECAB_PATH", "Y") == "Y", "not set"
