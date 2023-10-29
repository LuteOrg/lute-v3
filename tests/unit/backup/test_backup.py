"""
DB Backup tests.
"""

import os
import pytest
from datetime import datetime

from lute.backup.service import create_backup
from lute.models.setting import Setting


@pytest.fixture(name="bkp_dir")
def fixture_backup_directory(testconfig):
    "Create clean backup dir."
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
    backup_dir = os.path.join(base_dir, 'zz_bkp')
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


@pytest.fixture(name='backup_settings')
def fixture_backup_settings(testconfig, bkp_dir):
    ret = Setting.get_backup_settings()
    ret.backup_dir = bkp_dir
    ret.backup_enabled = 'y'


def test_backup_writes_file_to_output_dir(app_context, testconfig, bkp_dir, backup_settings):
    file_content = b'imagefile'
    img1 = os.path.join(testconfig.userimagespath, '1')
    if not os.path.exists(img1):
        os.mkdir(img1)
    with open(os.path.join(img1, 'file.txt'), 'wb') as f:
        f.write(file_content)

    create_backup(testconfig, backup_settings)
    assert len(os.listdir(bkp_dir)) == 1
    assert len(os.listdir(os.path.join(bkp_dir, 'userimages_backup', '1'))) == 1
    assert os.path.exists(os.path.join(bkp_dir, 'userimages_backup', '1', 'file.txt'))


### def test_timestamp_added_to_db_name(app_context, test_directories):
###     backup_dir, image_dir = test_directories
###     backup = SqliteBackup(config, SettingsRepository())
###     backup.create_db_backup()
###     files = os.listdir(backup_dir)
###     assert files == ['lute_backup_01.db.gz']
### 
### 
### def test_backup_fails_if_missing_output_dir(app_context, test_directories):
###     backup_dir, image_dir = test_directories
###     config['BACKUP_DIR'] = 'some_missing_dir'
###     backup = SqliteBackup(config, SettingsRepository())
###     with pytest.raises(Exception):
###         backup.create_backup()
### 
### 
### def test_user_can_configure_rolling_backup_count(app_context, test_directories):
###     backup_dir, image_dir = test_directories
###     config['BACKUP_COUNT'] = 2
###     backup = SqliteBackup(config, SettingsRepository())
###     for i in range(1, 10):
###         backup.create_db_backup(f'0{i}')
###     expected_files = [f'lute_backup_0{i}.db.gz' for i in range(8, 10)]
###     files = os.listdir(backup_dir)
###     assert files == expected_files
### 
### 
### def test_all_manual_backups_are_kept(app_context, test_directories):
###     backup_dir, image_dir = test_directories
###     config['BACKUP_COUNT'] = 2
###     manual_backups = True
###     backup = SqliteBackup(config, SettingsRepository(), manual_backups)
###     expected_files = []
###     for i in range(1, 10):
###         backup.create_db_backup(f'0{i}')
###         expected_files.append(f'manual_lute_backup_0{i}.db.gz')
###     files = os.listdir(backup_dir)
###     assert files == expected_files
### 
### 
### def test_last_import_setting_is_updated_on_successful_backup(app_context):
###     repo = SettingsRepository()
###     with pytest.raises(SettingsRepository.saveLastBackupDatetime):
###         config['BACKUP_ENABLED'] = 'yes'
###         backup = SqliteBackup(config, repo)
###         backup.create_backup()
### 
### 
### def test_should_not_run_autobackup_if_auto_is_no_or_false(app_context):
###     config['BACKUP_ENABLED'] = 'yes'
###     config['BACKUP_AUTO'] = 'no'
###     repo = SettingsRepository()
###     backup = SqliteBackup(config, repo)
###     with pytest.raises(SettingsRepository.getLastBackupDatetime):
###         assert backup.should_run_auto_backup() is False
### 
### 
### def test_checks_if_should_run_autobackup_if_auto_is_yes_or_true(app_context):
###     config['BACKUP_ENABLED'] = 'yes'
###     config['BACKUP_AUTO'] = 'yes'
###     repo = SettingsRepository()
###     backup = SqliteBackup(config, repo)
###     repo.getLastBackupDatetime = lambda: datetime.now().timestamp()
###     backup.should_run_auto_backup()
### 
### 
### def test_autobackup_returns_true_if_never_backed_up(app_context):
###     config['BACKUP_ENABLED'] = 'yes'
###     config['BACKUP_AUTO'] = 'yes'
###     repo = SettingsRepository()
###     repo.getLastBackupDatetime = lambda: None
###     backup = SqliteBackup(config, repo)
###     assert backup.should_run_auto_backup()
### 
### 
### def test_autobackup_returns_true_last_backed_up_over_one_day_ago(app_context):
###     config['BACKUP_ENABLED'] = 'yes'
###     config['BACKUP_AUTO'] = 'yes'
###     curr_datetime = datetime.now()
###     one_day_ago = curr_datetime.timestamp() - 24 * 60 * 60
### 
###     config['BACKUP_WARN'] = 'yes'
###     repo = SettingsRepository()
###     repo.getLastBackupDatetime = lambda: one_day_ago - 10
###     backup = SqliteBackup(config, repo)
###     assert backup.should_run_auto_backup() is True
### 
###     config['BACKUP_WARN'] = 'yes'
###     repo = SettingsRepository()
###     repo.getLastBackupDatetime = lambda: one_day_ago + 10
###     backup = SqliteBackup(config, repo)
###     assert backup.should_run_auto_backup() is False
### 
### 
### def test_warning_is_set_if_keys_missing(app_context):
###     config.clear()
###     backup = SqliteBackup(config, SettingsRepository())
###     expected = "Missing backup environment keys in .env: BACKUP_DIR, BACKUP_AUTO, BACKUP_WARN"
###     assert backup.warning() == expected
### 
### 
### def test_warn_if_last_backup_never_happened_or_is_old(app_context):
###     curr_datetime = datetime.now()
###     one_week_ago = curr_datetime.timestamp() - 7 * 24 * 60 * 60
### 
###     config['BACKUP_WARN'] = 'yes'
###     repo = SettingsRepository()
###     repo.getLastBackupDatetime = lambda: None
###     backup = SqliteBackup(config, repo)
###     assert backup.warning() == 'Last backup was more than 1 week ago'
### 
###     config['BACKUP_WARN'] = 'yes'
###     repo = SettingsRepository()
###     repo.getLastBackupDatetime = lambda: one_week_ago - 10
###     backup = SqliteBackup(config, repo)
###     assert backup.warning() == 'Last backup was more than 1 week ago'
### 
###     config['BACKUP_WARN'] = 'no'
###     repo = SettingsRepository()
###     repo.getLastBackupDatetime = lambda: one_week_ago - 10
###     backup = SqliteBackup(config, repo)
###     assert backup.warning() == ''
### 
###     config['BACKUP_WARN'] = 'yes'
###     repo = SettingsRepository()
###     repo.getLastBackupDatetime = lambda: one_week_ago + 10
###     backup = SqliteBackup(config, repo)
###     assert backup.warning() == ''

