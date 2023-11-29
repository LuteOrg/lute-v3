"""
Settings test.
"""

import os
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
