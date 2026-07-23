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

from lute.models.repositories import UserSettingRepository
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


class Service:
    "Service."

    def __init__(self, session):
        self.session = session

    def create_backup(self, app_config, settings, is_manual=False, suffix=None):
        """
        Create backup using current app config, settings.

        is_manual is True if this is a user-triggered manual
        backup, otherwise is False.

        suffix can be specified for test.

        settings are from BackupSettings.
          - backup_enabled
          - backup_dir
          - backup_auto
          - backup_warn
          - backup_count
          - last_backup_datetime
        """
        if not os.path.exists(settings.backup_dir):
            try:
                os.makedirs(settings.backup_dir, exist_ok=True)
            except OSError as e:
                raise BackupException(
                    f"Cannot create backup directory '{settings.backup_dir}': {e}. "
                    f"Please update your backup directory in Settings."
                ) from e

        # def _print_now(msg):
        #     "Timing helper for when implement audio backup."
        #     now = datetime.now().strftime("%H-%M-%S")
        #     print(f"{now} - {msg}", flush=True)

        self._mirror_images_dir(app_config.userimagespath, settings.backup_dir)

        prefix = "manual_" if is_manual else ""
        if suffix is None:
            suffix = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        fname = f"{prefix}lute_backup_{suffix}.db"
        backupfile = os.path.join(settings.backup_dir, fname)

        f = self._create_db_backup(app_config.dbfilename, backupfile)
        self._remove_excess_backups(settings.backup_count, settings.backup_dir)
        return f

    def should_run_auto_backup(self, backup_settings):
        """
        True (if applicable) if last backup was old.
        """
        bs = backup_settings
        if bs.backup_enabled is False or bs.backup_auto is False:
            return False

        if not bs.backup_dir or not os.path.exists(bs.backup_dir):
            try:
                parent_dir = os.path.dirname(bs.backup_dir)
                if not parent_dir or not os.access(parent_dir, os.W_OK):
                    return False
            except Exception:  # pylint: disable=broad-exception-caught
                return False

        last = bs.last_backup_datetime
        if last is None:
            return True

        curr = int(time.time())
        diff = curr - last
        return diff > 24 * 60 * 60

    def backup_warning(self, backup_settings):
        "Get warning if needed."
        if not backup_settings.backup_warn:
            return ""

        have_books = self.session.query(self.session.query(Book).exists()).scalar()
        have_terms = self.session.query(self.session.query(Term).exists()).scalar()
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

    def _create_db_backup(self, dbfilename, backupfile):
        "Make a backup."
        shutil.copy(dbfilename, backupfile)
        f = f"{backupfile}.gz"
        with open(backupfile, "rb") as in_file, gzip.open(
            f, "wb", compresslevel=4
        ) as out_file:
            shutil.copyfileobj(in_file, out_file)
        os.remove(backupfile)
        r = UserSettingRepository(self.session)
        r.set_last_backup_datetime(int(time.time()))
        return f

    def skip_this_backup(self):
        "Set the last backup time to today."
        r = UserSettingRepository(self.session)
        r.set_last_backup_datetime(int(time.time()))

    def _remove_excess_backups(self, count, outdir):
        "Remove old backups."
        files = [f for f in self.list_backups(outdir) if not f.is_manual]
        files.sort(reverse=True)
        to_remove = files[count:]
        for f in to_remove:
            os.remove(f.filepath)

    def _mirror_images_dir(self, userimagespath, outdir):
        "Copy the images to backup."
        target_dir = os.path.join(outdir, "userimages_backup")
        target_dir = os.path.abspath(target_dir)
        if not os.path.exists(target_dir):
            os.mkdir(target_dir)
        shutil.copytree(userimagespath, target_dir, dirs_exist_ok=True)

    def _add_missing_default_settings(self, dbfilename, app_config, current_backup_dir=None, current_mecab_path=None):
        """
        Add any missing default user settings to the database at dbfilename.

        Uses raw sqlite3 to avoid messing with the SQLAlchemy session
        (which was disposed before the db file was replaced).

        If current_backup_dir is provided, it will be preserved in the
        restored database (so the user's backup directory preference
        isn't overwritten by the backup's setting).
        """
        import sqlite3

        default_tts_settings = [
            ("tts_enabled", "1"),
            ("tts_hover_pronunciation", "1"),
            ("tts_click_pronunciation", "1"),
            ("tts_show_control_panel", "1"),
            ("tts_show_sentence_buttons", "1"),
            ("current_language_id", "0"),
        ]

        conn = sqlite3.connect(dbfilename)
        try:
            cursor = conn.cursor()
            for key, default_value in default_tts_settings:
                cursor.execute(
                    "SELECT StValue FROM settings WHERE StKey = ? AND StKeyType = 'user'",
                    (key,),
                )
                row = cursor.fetchone()
                if row is None:
                    cursor.execute(
                        "INSERT INTO settings (StKey, StValue, StKeyType) VALUES (?, ?, 'user')",
                        (key, default_value),
                    )

            # Preserve the current backup_dir from before restore
            if current_backup_dir:
                cursor.execute(
                    "SELECT StValue FROM settings WHERE StKey = 'backup_dir' AND StKeyType = 'user'"
                )
                row = cursor.fetchone()
                if row is None:
                    cursor.execute(
                        "INSERT INTO settings (StKey, StValue, StKeyType) VALUES ('backup_dir', ?, 'user')",
                        (current_backup_dir,),
                    )
                else:
                    cursor.execute(
                        "UPDATE settings SET StValue = ? WHERE StKey = 'backup_dir' AND StKeyType = 'user'",
                        (current_backup_dir,),
                    )

            # Preserve the current mecab_path from before restore
            # (system-specific path, shouldn't be overwritten by backup)
            if current_mecab_path:
                cursor.execute(
                    "SELECT StValue FROM settings WHERE StKey = 'mecab_path' AND StKeyType = 'user'"
                )
                row = cursor.fetchone()
                if row is None:
                    cursor.execute(
                        "INSERT INTO settings (StKey, StValue, StKeyType) VALUES ('mecab_path', ?, 'user')",
                        (current_mecab_path,),
                    )
                else:
                    cursor.execute(
                        "UPDATE settings SET StValue = ? WHERE StKey = 'mecab_path' AND StKeyType = 'user'",
                        (current_mecab_path,),
                    )

            conn.commit()
        finally:
            conn.close()

    def list_backups(self, outdir) -> List[DatabaseBackupFile]:
        "List all backup files."
        if not os.path.exists(outdir):
            return []
        return [
            DatabaseBackupFile(os.path.join(outdir, f))
            for f in os.listdir(outdir)
            if re.match(r"(manual_)?lute_backup_", f)
        ]

    # Module-level flag to signal that the engine needs resetting.
    # Set by restore_backup(), checked in before_request handler.
    _engine_needs_reset = False

    def restore_backup(self, app_config, backup_file_path):
        """
        Restore from a backup file.

        backup_file_path can be either a .db.gz file or a .db file.
        DANGEROUS: this replaces the current database.
        """
        import sqlite3
        import tempfile

        if not os.path.exists(backup_file_path):
            raise BackupException(f"Backup file not found: {backup_file_path}")

        # Use raw sqlite3 to read current system-specific settings.
        # These should NOT be overwritten by the backup because they're
        # specific to the current system (paths, etc.)
        current_db = app_config.dbfilename
        preserved_settings = {}
        settings_to_preserve = ["backup_dir", "mecab_path"]
        try:
            conn = sqlite3.connect(current_db)
            cursor = conn.cursor()
            for key in settings_to_preserve:
                cursor.execute(
                    "SELECT StValue FROM settings WHERE StKey = ? AND StKeyType = 'user'",
                    (key,),
                )
                row = cursor.fetchone()
                if row:
                    preserved_settings[key] = row[0]
            conn.close()
        except Exception:  # pylint: disable=broad-exception-caught
            pass

        current_backup_dir = preserved_settings.get("backup_dir")
        current_mecab_path = preserved_settings.get("mecab_path")

        # Determine if it's gzipped
        is_gz = backup_file_path.endswith(".gz")

        # Extract to temp file if gzipped
        db_file_to_restore = backup_file_path
        temp_dir = None
        if is_gz:
            temp_dir = tempfile.mkdtemp()
            db_file_to_restore = os.path.join(temp_dir, "restored.db")
            with gzip.open(backup_file_path, "rb") as f_in, \
                 open(db_file_to_restore, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)

        try:
            # Verify it's a valid Lute database by checking for key tables
            conn = sqlite3.connect(db_file_to_restore)
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='settings'"
                )
                if not cursor.fetchone():
                    raise BackupException(
                        "Invalid backup file: missing 'settings' table. "
                        "This does not appear to be a Lute backup."
                    )
            finally:
                conn.close()

            # Backup current database first (safety copy)
            safety_copy = current_db + ".pre_restore_" + \
                datetime.now().strftime("%Y%m%d_%H%M%S")
            shutil.copy2(current_db, safety_copy)

            # Replace current database with restored one
            shutil.copy2(db_file_to_restore, current_db)

            # Add any missing default user settings to the restored db,
            # and preserve system-specific settings (backup_dir, mecab_path).
            self._add_missing_default_settings(
                current_db, app_config,
                current_backup_dir=current_backup_dir,
                current_mecab_path=current_mecab_path,
            )

            # Set flag so the next request will reset the engine cleanly.
            Service._engine_needs_reset = True

            return safety_copy
        finally:
            # Clean up temp dir
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
