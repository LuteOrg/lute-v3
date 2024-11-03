"""
Settings test.
"""

from unittest.mock import patch
import pytest
from lute.db import db
from lute.models.repositories import (
    UserSettingRepository,
    SystemSettingRepository,
    MissingUserSettingKeyException,
)
from tests.dbasserts import assert_sql_result


@pytest.fixture(name="us_repo")
def fixture_usersetting_repo(app_context):
    "Repo"
    r = UserSettingRepository(db.session)
    return r


@pytest.fixture(name="ss_repo")
def fixture_systemsetting_repo(app_context):
    "Repo"
    r = SystemSettingRepository(db.session)
    return r


def test_user_and_system_settings_do_not_intersect(us_repo, ss_repo):
    "A UserSetting is not available as a system setting."
    us_repo.set_value("backup_count", 42)
    db.session.commit()
    sql = "select StValue, StKeyType from settings where StKey = 'backup_count'"
    assert_sql_result(sql, ["42; user"], "loaded")
    u = us_repo.get_value("backup_count")
    assert u == "42", "found user setting"
    assert ss_repo.get_value("backup_count") is None, "not in system settings"


def test_save_and_retrieve_user_setting(us_repo):
    "Smoke tests."
    us_repo.set_value("backup_count", 42)
    sql = "select StValue from settings where StKey = 'backup_count'"
    assert_sql_result(sql, ["5"], "still default")

    db.session.commit()
    assert_sql_result(sql, ["42"], "now set")

    v = us_repo.get_value("backup_count")
    assert v == "42", "is string"


def test_missing_value_value_is_null(ss_repo):
    "Missing key = None."
    assert ss_repo.get_value("missing") is None, "missing key"


def test_smoke_last_backup(us_repo):
    "Check syntax only."
    v = us_repo.get_last_backup_datetime()
    assert v is None, "not set"

    us_repo.set_last_backup_datetime(42)
    v = us_repo.get_last_backup_datetime()
    assert v == 42, "set _and_ saved"


def test_get_backup_settings(us_repo):
    "Smoke test."
    us_repo.set_value("backup_dir", "blah")
    us_repo.set_value("backup_count", 12)
    us_repo.set_value("backup_warn", 0)
    db.session.commit()
    b = us_repo.get_backup_settings()
    assert b.backup_dir == "blah"
    assert b.backup_auto is True  # initial defaults
    assert b.backup_warn is False  # set to 0 above
    assert b.backup_count == 12
    assert b.last_backup_datetime is None


def test_time_since_last_backup_future(us_repo):
    """
    Check formatting when last backup is reported to be in the future.

    current time = 600, backup time = 900
    """
    b = us_repo.get_backup_settings()
    with patch("time.time", return_value=600):
        b.last_backup_datetime = 900
        assert b.time_since_last_backup is None


def test_time_since_last_backup_none(us_repo):
    """
    Check formatting when last backup is reported to be None.

    current time = 600, backup time = None
    """
    b = us_repo.get_backup_settings()
    with patch("time.time", return_value=600):
        b.last_backup_datetime = None
        assert b.time_since_last_backup is None


def test_time_since_last_backup_right_now(us_repo):
    """
    Check formatting when last backup is reported to be the same as current time.

    current time = 600, backup time = 600
    """
    b = us_repo.get_backup_settings()
    with patch("time.time", return_value=600):
        b.last_backup_datetime = 600
        assert b.time_since_last_backup == "0 seconds ago"


def test_time_since_last_backup_in_past(us_repo):
    """
    Check formatting when last backup is reported to be in the past.

    current time = 62899200, backup time = various
    """
    b = us_repo.get_backup_settings()
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


def test_get_or_set_user_setting_unknown_key_throws(us_repo):
    "Safety, ensure no typo for user settings."
    with pytest.raises(MissingUserSettingKeyException):
        us_repo.get_value("bad_key")
    with pytest.raises(MissingUserSettingKeyException):
        us_repo.set_value("bad_key", 17)
