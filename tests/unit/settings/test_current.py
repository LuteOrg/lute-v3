"""
Current settings tests.
"""

import pytest
from sqlalchemy import text
from lute.db import db
from lute.models.setting import (
    UserSettingRepository,
    BackupSettings,
)
from lute.settings.current import load, refresh_global_settings, current_settings


@pytest.fixture(name="us_repo")
def fixture_usersetting_repo(app_context):
    "Repo"
    r = UserSettingRepository(db.session)
    return r


def test_load_refreshes_current_settings(app_context):
    "Current settigns are loaded."
    if "backup_dir" in current_settings:
        del current_settings["backup_dir"]
    load(db.session, "blah")
    assert "backup_dir" in current_settings, "loaded"


def test_refresh_refreshes_current_settings(app_context):
    "Current settigns are loaded."
    if "backup_dir" in current_settings:
        del current_settings["backup_dir"]
    refresh_global_settings(db.session)
    assert "backup_dir" in current_settings, "loaded"


def test_user_settings_loaded_with_defaults(us_repo):
    "Called on load."
    db.session.execute(text("delete from settings"))
    db.session.commit()
    assert us_repo.key_exists("backup_dir") is False, "key removed"
    load(db.session, "blah")
    assert us_repo.key_exists("backup_dir") is True, "key created"

    # Check defaults
    b = BackupSettings(db.session)
    assert b.backup_enabled is True
    assert b.backup_dir is not None
    assert b.backup_auto is True
    assert b.backup_warn is True
    assert b.backup_count == 5


def test_user_settings_load_leaves_existing_values(us_repo):
    "Called on load."
    us_repo.set_value("backup_count", 17)
    db.session.commit()
    assert us_repo.get_value("backup_count") == "17"
    load(db.session, "blah")
    b = BackupSettings(db.session)
    assert b.backup_count == 17, "still 17"
