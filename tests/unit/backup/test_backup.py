"""
DB Backup tests.
"""

import os
from datetime import datetime
import pytest

from lute.backup.service import (
    create_backup,
    BackupException,
    should_run_auto_backup,
    backup_warning,
)
from lute.models.setting import BackupSettings

# pylint: disable=missing-function-docstring
# Test method names are pretty descriptive already.


@pytest.fixture(name="bkp_dir")
def fixture_backup_directory(testconfig):
    "Create clean backup dir."
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    backup_dir = os.path.join(base_dir, "zz_bkp")
    if not os.path.exists(backup_dir):
        os.mkdir(backup_dir)

    # Cleanup prior to test.
    cleanup_directory(backup_dir)
    cleanup_directory(testconfig.userimagespath)

    yield backup_dir

    # Don't clean up after the test, in case want to check manually.
    # cleanup_directories(backup_dir, image_dir)


def cleanup_directory(directory):
    "Delete all files and subfolders."
    for root, dirs, files in os.walk(directory, topdown=False):
        for f in files:
            os.remove(os.path.join(root, f))
        for d in dirs:
            os.rmdir(os.path.join(root, d))


@pytest.fixture(name="backup_settings")
def fixture_backup_settings(app_context, bkp_dir):
    # app_context is passed so that the db session is available.
    ret = BackupSettings.get_backup_settings()
    ret.backup_dir = bkp_dir
    ret.backup_enabled = True
    yield ret


def test_backup_writes_file_to_output_dir(testconfig, bkp_dir, backup_settings):
    file_content = b"imagefile"
    img1 = os.path.join(testconfig.userimagespath, "1")
    if not os.path.exists(img1):
        os.mkdir(img1)
    with open(os.path.join(img1, "file.txt"), "wb") as f:
        f.write(file_content)

    create_backup(testconfig, backup_settings)
    assert len(os.listdir(bkp_dir)) == 2  # db and directory
    assert len(os.listdir(os.path.join(bkp_dir, "userimages_backup", "1"))) == 1
    assert os.path.exists(os.path.join(bkp_dir, "userimages_backup", "1", "file.txt"))


def test_timestamp_added_to_db_name(testconfig, bkp_dir, backup_settings):
    assert os.listdir(bkp_dir) == [], "empty dirs at start"
    create_backup(testconfig, backup_settings)
    dbfile = [f for f in os.listdir(bkp_dir) if f.startswith("lute_backup_2")]
    assert len(dbfile) == 1, "db found"


def test_backup_fails_if_missing_output_dir(testconfig, backup_settings):
    backup_settings.backup_dir = "some_missing_dir"
    with pytest.raises(BackupException, match="Missing directory some_missing_dir"):
        create_backup(testconfig, backup_settings)


def test_user_can_configure_rolling_backup_count(testconfig, bkp_dir, backup_settings):
    backup_settings.backup_count = 2
    for i in range(1, 10):
        create_backup(testconfig, backup_settings, suffix=f"0{i}")
    expected_files = [f"lute_backup_0{i}.db.gz" for i in range(8, 10)]
    db_files = [f for f in os.listdir(bkp_dir) if f.endswith(".gz")]
    assert db_files.sort() == expected_files.sort()


def test_all_manual_backups_are_kept(testconfig, bkp_dir, backup_settings):
    backup_settings.backup_count = 2
    for i in range(1, 10):
        create_backup(testconfig, backup_settings, suffix=f"0{i}", is_manual=True)
    expected_files = [f"lute_backup_0{i}.db.gz" for i in range(1, 10)]
    db_files = [f for f in os.listdir(bkp_dir) if f.endswith(".gz")]
    assert db_files.sort() == expected_files.sort()


def test_last_import_setting_is_updated_on_successful_backup(
    testconfig, backup_settings
):
    assert backup_settings.last_backup_datetime is None, "no backup"
    create_backup(testconfig, backup_settings)
    updated = BackupSettings.get_backup_settings()
    assert updated.last_backup_datetime is not None, "set"


def test_should_not_run_autobackup_if_auto_is_no_or_false(backup_settings):
    backup_settings.backup_enabled = True
    backup_settings.backup_auto = False
    assert should_run_auto_backup(backup_settings) is False


def test_autobackup_returns_true_if_never_backed_up(backup_settings):
    backup_settings.backup_enabled = True
    backup_settings.backup_auto = True
    backup_settings.last_backup_datetime = None
    assert should_run_auto_backup(backup_settings) is True


def test_autobackup_returns_true_if_last_backed_up_over_one_day_ago(backup_settings):
    backup_settings.backup_auto = True
    # backup_settings.backup_warn = True
    curr_datetime = datetime.now()
    one_day_ago = curr_datetime.timestamp() - 24 * 60 * 60

    backup_settings.last_backup_datetime = one_day_ago - 10
    assert should_run_auto_backup(backup_settings) is True

    backup_settings.last_backup_datetime = one_day_ago + 10
    assert should_run_auto_backup(backup_settings) is False


def test_warn_if_last_backup_never_happened_or_is_old(backup_settings):
    curr_datetime = datetime.now()
    one_week_ago = curr_datetime.timestamp() - 7 * 24 * 60 * 60

    backup_settings.backup_warn = True
    backup_settings.last_backup_datetime = None
    assert backup_warning(backup_settings) == "Never backed up."

    backup_settings.last_backup_datetime = one_week_ago + 10
    assert backup_warning(backup_settings) == ""

    backup_settings.last_backup_datetime = one_week_ago - 10
    assert backup_warning(backup_settings) == "Last backup was more than 1 week ago."

    backup_settings.backup_warn = False
    assert backup_warning(backup_settings) == ""
