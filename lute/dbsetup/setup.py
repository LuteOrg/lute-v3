"""
Database setup.

Creates database if necessary.
Runs migrations.
Manages backups pre-migration.a
"""

import os

class Setup: # pylint: disable=too-few-public-methods
    """
    Main setup class, coordinates other classes.
    """

    def __init__(
            self,
            db_filename: str,
            backup_folder: str,
            migration_files: dict
    ):
        self._db_filename = db_filename
        self._backup_folder = backup_folder
        self._migrations = migration_files


    def setup(self):
        """
        Do database setup, making backup if necessary, running migrations.
        """

        if not os.path.exists(self._db_filename):
            self._create_baseline()


    def _create_baseline(self):
        """
        Create baseline database.
        """
        # get connection, run script
