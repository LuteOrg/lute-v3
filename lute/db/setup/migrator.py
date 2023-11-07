"""
Database migration manager.

Runs migrations and logs them to a _migrations table so they aren't
run twice.  Runs repeatable migrations always.
"""

import os
from contextlib import contextmanager


@contextmanager
def _change_directory(new_dir):
    "Change directory, and return to the current dir when done."
    old_dir = os.getcwd()
    try:
        os.chdir(new_dir)
        yield
    finally:
        os.chdir(old_dir)


class SqliteMigrator:
    """
    Sqlite migrator class.

    Follows the principles documented in
    https://github.com/jzohrab/DbMigrator/blob/master/docs/managing_database_changes.md
    """

    def __init__(self, location, repeatable):
        self.location = location
        self.repeatable = repeatable

    def has_migrations(self, conn):
        """
        Return True if have non-applied migrations.
        """
        outstanding = self._get_pending(conn)
        return len(outstanding) > 0

    def _get_pending(self, conn):
        """
        Get all non-applied (one-time) migrations.
        """
        allfiles = []
        with _change_directory(self.location):
            allfiles = [
                os.path.join(self.location, s)
                for s in os.listdir()
                if s.endswith(".sql")
            ]
            allfiles.sort()
            outstanding = [f for f in allfiles if self._should_apply(conn, f)]
        return outstanding

    def do_migration(self, conn):
        """
        Run all migrations, then all repeatable migrations.
        """
        self._process_folder(conn)
        self._process_repeatable(conn)

    def _process_folder(self, conn):
        """
        Run all pending migrations.  Write executed script to
        _migrations table.
        """
        outstanding = self._get_pending(conn)
        for f in outstanding:
            try:
                self._process_file(conn, f)
            except Exception as e:
                msg = str(e)
                print(f"\nFile {f} exception:\n{msg}\n")
                raise e
            self._add_migration_to_database(conn, f)

    def _process_repeatable(self, conn):
        """
        Run all repeatable migrations.
        """
        with _change_directory(self.repeatable):
            files = [
                os.path.join(self.repeatable, f)
                for f in os.listdir()
                if f.endswith(".sql")
            ]
        for f in files:
            try:
                self._process_file(conn, f)
            except Exception as e:
                msg = str(e)
                print(f"\nFile {f} exception:\n{msg}\n")
                raise e

    def _should_apply(self, conn, filename):
        """
        True if a migration hasn't been run yet.

        The file basename (no directory) is stored in the migration table.
        """
        f = os.path.basename(filename)
        sql = f"select count(filename) from _migrations where filename = '{f}'"
        res = conn.execute(sql).fetchone()
        return res[0] == 0

    def _add_migration_to_database(self, conn, filename):
        """
        Track the executed migration in _migrations.
        """
        f = os.path.basename(filename)
        conn.execute("begin transaction")
        conn.execute(f"INSERT INTO _migrations values ('{f}')")
        conn.execute("commit transaction")

    def _process_file(self, conn, f):
        """
        Run the given file.
        """
        with open(f, "r", encoding="utf8") as sql_file:
            commands = sql_file.read()
            self._exec_commands(conn, commands)

    def _exec_commands(self, conn, sql):
        """
        Execute all commands in the given file.
        """
        conn.executescript(sql)
