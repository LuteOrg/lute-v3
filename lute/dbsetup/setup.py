"""
Database setup.

Creates database if necessary.
Runs migrations.
Manages backups pre-migration.a
"""

class Setup: # pylint: disable=too-few-public-methods
    """
    Main setup class, coordinates other classes.
    """

    def __init__(self, db_filename, backup_folder, migrations_folder, repeatable_migrations_folder):
        pass

    def setup(self):
        """
        Do database setup, making backup if necessary, running migrations.
        """
