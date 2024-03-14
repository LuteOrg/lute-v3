"""
Db and image backup.
"""

import os
import re
import shutil
import gzip
from datetime import datetime
import time
from typing import List, Union

from lute.db import db
from lute.models.setting import SystemSetting
from lute.models.book import Book
from lute.models.term import Term


class BackupException(Exception):
    """
    Raised if export bombs for some reason.
    """


class DatabaseBackupFile:
    """
    A representation of a lute backup file to hold metadata attributes.
    """

    def __init__(self, filepath: Union[str, os.PathLike]):
        if not os.path.exists(filepath):
            raise BackupException(f"No backup file at {filepath}.")

        name = os.path.basename(filepath)
        if not re.match(r"(manual_)?lute_backup_", name):
            raise BackupException(f"Not a valid lute database backup at {filepath}.")

        self.filepath = filepath
        self.name = name
        self.is_manual = self.name.startswith("manual_")

    def __lt__(self, other):
        return self.last_modified < other.last_modified

    @property
    def last_modified(self) -> datetime:
        return datetime.fromtimestamp(os.path.getmtime(self.filepath)).astimezone()

    @property
    def size_bytes(self) -> int:
        return os.path.getsize(self.filepath)

    @property
    def size(self) -> str:
        """
        A human-readable string representation of the size of the file.

        Eg.
        1746 bytes
        4 kB
        27 MB
        """
        s = self.size_bytes
        if s >= 1e9:
            return f"{round(s * 1e-9)} GB"
        if s >= 1e6:
            return f"{round(s * 1e-6)} MB"
        if s >= 1e3:
            return f"{round(s * 1e-3)} KB"
        return f"{s} bytes"


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

    ### Timing helper for when implement audio backup.
    # def _print_now(msg):
    #     now = datetime.now().strftime("%H-%M-%S")
    #     print(f"{now} - {msg}", flush=True)

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
    bs = backup_settings
    if bs.backup_enabled is False or bs.backup_auto is False:
        return False

    last = bs.last_backup_datetime
    if last is None:
        return True

    curr = int(time.time())
    diff = curr - last
    return diff > 24 * 60 * 60


def backup_warning(backup_settings):
    "Get warning if needed."
    if not backup_settings.backup_warn:
        return ""

    have_books = db.session.query(db.session.query(Book).exists()).scalar()
    have_terms = db.session.query(db.session.query(Term).exists()).scalar()
    if have_books is False and have_terms is False:
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
        f, "wb", compresslevel=4
    ) as out_file:
        shutil.copyfileobj(in_file, out_file)
    os.remove(backupfile)
    SystemSetting.set_last_backup_datetime(int(time.time()))
    return f


def skip_this_backup():
    "Set the last backup time to today."
    SystemSetting.set_last_backup_datetime(int(time.time()))


def _remove_excess_backups(count, outdir):
    "Remove old backups."
    files = [f for f in list_backups(outdir) if not f.is_manual]
    files.sort(reverse=True)
    to_remove = files[count:]
    for f in to_remove:
        os.remove(f.filepath)


def _mirror_images_dir(userimagespath, outdir):
    "Copy the images to backup."
    target_dir = os.path.join(outdir, "userimages_backup")
    target_dir = os.path.abspath(target_dir)
    if not os.path.exists(target_dir):
        os.mkdir(target_dir)
    shutil.copytree(userimagespath, target_dir, dirs_exist_ok=True)


def list_backups(outdir) -> List[DatabaseBackupFile]:
    "List all backup files."
    return [
        DatabaseBackupFile(os.path.join(outdir, f))
        for f in os.listdir(outdir)
        if re.match(r"(manual_)?lute_backup_", f)
    ]
