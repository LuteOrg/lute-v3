"""
Db and image backup.
"""

import os
import shutil
import gzip
from datetime import datetime
import time

from lute.models.setting import SystemSetting


class BackupException(Exception):
    """
    Raised if export bombs for some reason.
    """


def create_backup(app_config, settings, is_manual=False, suffix=None):
    """
    Create backup using current app config, settings.

    is_manual is True if this is a user-triggered manual
    backup, otherwise is False.

    suffix can be specified for test.

    settings are from Setting.get_backup_settings().
      - backup_enabled
      - backup_dir
      - backup_auto
      - backup_warn
      - backup_count
      - last_backup_datetime
    """
    if not os.path.exists(settings.backup_dir):
        raise BackupException("Missing directory " + settings.backup_dir)

    _mirror_images_dir(app_config.userimagespath, settings.backup_dir)

    prefix = "manual_" if is_manual else ""
    if suffix is None:
        suffix = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    fname = f"{prefix}lute_backup_{suffix}.db"
    backupfile = os.path.join(settings.backup_dir, fname)

    f = _create_db_backup(app_config.dbfilename, backupfile)
    _remove_excess_backups(settings.backup_count, settings.backup_dir)
    return f


def should_run_auto_backup(backup_settings):
    """
    True (if applicable) if last backup was old.
    """
    if backup_settings.backup_enabled != "y" or not backup_settings.backup_auto:
        return False

    last = backup_settings.last_backup_datetime
    if last is None:
        return True

    curr = int(time.time())
    diff = curr - last
    return diff > 24 * 60 * 60


def backup_warning(backup_settings):
    "Get warning if needed."
    if not backup_settings.backup_warn:
        return ""

    last = backup_settings.last_backup_datetime
    if last is None:
        return "Never backed up."

    curr = int(time.time())
    diff = curr - last
    old_backup_msg = "Last backup was more than 1 week ago."
    if diff > 7 * 24 * 60 * 60:
        return old_backup_msg

    return ""


def _create_db_backup(dbfilename, backupfile):
    "Make a backup."
    shutil.copy(dbfilename, backupfile)
    f = f"{backupfile}.gz"
    with open(backupfile, "rb") as in_file, gzip.open(
        f, "wb", compresslevel=9
    ) as out_file:
        shutil.copyfileobj(in_file, out_file)
    os.remove(backupfile)
    SystemSetting.set_last_backup_datetime(int(time.time()))
    return f


def _remove_excess_backups(count, outdir):
    "Remove old backups."
    files = [f for f in os.listdir(outdir) if f.startswith("lute_backup_")]
    files.sort(reverse=True)
    to_remove = files[count:]
    for f in to_remove:
        os.remove(os.path.join(outdir, f))


def _mirror_images_dir(userimagespath, outdir):
    "Copy the images to backup."
    target_dir = os.path.join(outdir, "userimages_backup")
    target_dir = os.path.abspath(target_dir)
    if not os.path.exists(target_dir):
        os.mkdir(target_dir)
    shutil.copytree(userimagespath, target_dir, dirs_exist_ok=True)
