"""
Database setup.

Creates database if necessary.
Runs migrations.
Manages backups pre-migration.a
"""

from contextlib import closing
import os
import sqlite3
import gzip
import shutil
from datetime import datetime
import glob

from .migrator import SqliteMigrator


class BackupManager: # pylint: disable=too-few-public-methods
    """
    Creates db backups when needed, prunes old backups.
    """

    def __init__(self, file_to_backup, backup_directory, max_number_of_backups):
        self.file_to_backup = file_to_backup
        self.backup_directory = backup_directory
        self.max_number_of_backups = max_number_of_backups

    def do_backup(self, next_backup_datetime = None):
        """
        Perform the db file backup to backup_dir,
        pruning old backups.
        """

        if next_backup_datetime is None:
            now = datetime.now()
            next_backup_datetime = now.strftime("%Y%m%d-%H%M%S-%f")

        bname = os.path.basename(self.file_to_backup)
        backup_filename = f'{bname}.{next_backup_datetime}.gz'
        backup_path = os.path.join(self.backup_directory, backup_filename)

        os.makedirs(self.backup_directory, exist_ok=True)

        # Copy the file to the backup directory and gzip it
        with open(self.file_to_backup, 'rb') as source_file, \
             gzip.open(backup_path, 'wb') as backup_file:
            shutil.copyfileobj(source_file, backup_file)
        assert os.path.exists(backup_path)

        # List all backup files in the directory, sorted by name.
        # Since this includes the timestamp, the oldest files will be
        # listed first.
        globname = f'{bname}.*.gz'
        globpath = os.path.join(self.backup_directory, globname)
        backup_files = glob.glob(globpath)
        backup_files.sort(key=os.path.basename)

        # Delete excess backup files if necessary
        while len(backup_files) > self.max_number_of_backups:
            file_to_delete = backup_files.pop(0)
            os.remove(file_to_delete)


class Setup: # pylint: disable=too-few-public-methods
    """
    Main setup class, coordinates other classes.
    """

    def __init__(
            self,
            db_filename: str,
            baseline_schema_file: str,
            backup_manager: BackupManager,
            migrator: SqliteMigrator
    ):
        self._db_filename = db_filename
        self._baseline_schema_file = baseline_schema_file
        self._backup_mgr = backup_manager
        self._migrator = migrator


    def setup(self):
        """
        Do database setup, making backup if necessary, running migrations.
        """
        new_db = False
        if not os.path.exists(self._db_filename):
            new_db = True
            self._create_baseline()
        self._run_migrations()
        if not new_db:
            self._backup_mgr.do_backup()


    def _open_connection(self):
        """
        Get connection to db_filename.  Callers must close.
        """
        return sqlite3.connect(
            self._db_filename,
            detect_types=sqlite3.PARSE_DECLTYPES
        )


    def _create_baseline(self):
        """
        Create baseline database.
        """
        b = self._baseline_schema_file
        with open(b, 'r', encoding='utf8') as f:
            sql = f.read()
        with closing(self._open_connection()) as conn:
            conn.executescript(sql)


    def _run_migrations(self):
        """
        Migrate the db.  Return true if migrations were applied.
        Note this returns False if only non-repeatable migrations were applied!
        """
        has_migs = False
        with closing(self._open_connection()) as conn:
            has_migs = self._migrator.has_migrations(conn)
            self._migrator.do_migration(conn)
        return has_migs
