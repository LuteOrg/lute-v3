"""
Database setup.

Creates database if necessary.
Runs migrations.
Manages backups pre-migration.a
"""

from contextlib import closing
import os
import sqlite3

from .migrator import SqliteMigrator


class BackupManager: # pylint: disable=too-few-public-methods
    """
    Creates db backups when needed, prunes old backups.
    """

    def __init__(
        self,
        dbfile,
        backup_dir,
        next_backup_filename,
        backup_count
    ):
        pass

    def handle_backup(self):
        """
        Perform the db file backup to backup_dir,
        pruning old backups.
        """


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
        has_migrations = False
        if not os.path.exists(self._db_filename):
            new_db = True
            self._create_baseline()
        has_migrations = self._run_migrations()
        if not new_db and has_migrations:
            self._backup_mgr.handle_backup()


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
        Migrate the db.  Return true if migrations were run, else false.
        """
        has_migs = False
        with closing(self._open_connection()) as conn:
            has_migs = self._migrator.has_migrations(conn)
            if has_migs:
                self._migrator.do_migration(conn)
        return has_migs
