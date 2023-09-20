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
            backup_manager,
            migration_files: dict
    ):
        self._db_filename = db_filename
        self._backup_mgr = backup_manager
        self._migrations = migration_files


    def setup(self):
        """
        Do database setup, making backup if necessary, running migrations.
        """

        if not os.path.exists(self._db_filename):
            self._create_baseline()
        self._run_migrations()
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
        b = self._migrations['baseline']
        with open(b, 'r', encoding='utf8') as f:
            sql = f.read()
        with closing(self._open_connection()) as conn:
            conn.executescript(sql)


    def _run_migrations(self):
        """
        Migrate the db.
        """
        def get_valid_folder(fname):
            f = self._migrations[fname]
            if f is None:
                raise RuntimeError(f'Missing key {fname}')
            if not os.path.exists(f):
                raise RuntimeError(f'Missing required folder {f}')
            return f

        migrations = get_valid_folder('migrations')
        repeatable = get_valid_folder('repeatable')

        with closing(self._open_connection()) as conn:
            migrator = SqliteMigrator(conn, migrations, repeatable)
            migrator.process()
