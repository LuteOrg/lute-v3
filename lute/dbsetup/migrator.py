"""
Database migration manager.

Runs migrations and logs them to a _migrations table so they aren't
run twice.  Runs repeatable migrations always.
"""

import os

class SqliteMigrator:
    """
    Sqlite migrator class.

    Follows the principles documented in
    https://github.com/jzohrab/DbMigrator/blob/master/docs/managing_database_changes.md
    """

    def __init__(self, conn, location, repeatable, showlogging=False):
        self.conn = conn
        self.location = location
        self.repeatable = repeatable
        self.showlogging = showlogging

    def get_pending(self):
        """
        Get all non-applied (one-time) migrations.
        """
        allfiles = []
        os.chdir(self.location)
        allfiles = [s for s in os.listdir() if s.endswith('.sql')]
        allfiles.sort()
        outstanding = [f for f in allfiles if self._should_apply(f)]
        return outstanding

    def process(self):
        """
        Run all migrations, then all repeatable migrations.
        """
        self._process_folder()
        self._process_repeatable()

    def _log(self, message):
        """
        Hacky debug logging.
        """
        if self.showlogging:
            print(message)

    def _process_folder(self):
        """
        Run all pending migrations.  Write executed script to
        _migrations table.
        """
        outstanding = self.get_pending()
        self._log(f"running {len(outstanding)} migrations in {self.location}")
        for f in outstanding:
            try:
                self._process_file(f)
            except Exception as e:
                msg = str(e)
                print(f"\nFile {f} exception:\n{msg}\n")
                raise e
            self._add_migration_to_database(f)

    def _process_repeatable(self):
        """
        Run all repeatable migrations.
        """
        folder = self.repeatable
        os.chdir(folder)
        files = [f for f in os.listdir() if f.endswith('.sql')]
        self._log(f"running {len(files)} repeatable migrations in {folder}")
        for f in files:
            try:
                self._process_file(f, False)
            except Exception as e:
                msg = str(e)
                print(f"\nFile {f} exception:\n{msg}\n")
                raise e

    def _should_apply(self, filename):
        """
        True if a migration hasn't been run yet.
        """
        if os.path.isdir(filename):
            return False
        sql = f"select count(filename) from _migrations where filename = '{filename}'"
        res = self.conn.execute(sql).fetchone()
        return res[0] == 0

    def _add_migration_to_database(self, filename):
        """
        Track the executed migration in _migrations.
        """
        self._log(f'  tracking migration {filename}')
        self.conn.execute('begin transaction')
        self.conn.execute(f"INSERT INTO _migrations values ('{filename}')")
        self.conn.execute('commit transaction')

    def _process_file(self, f, showmsg=True):
        """
        Run the given file.
        """
        if showmsg:
            self._log(f"  running {f}")
        with open(f, 'r', encoding='utf8') as sql_file:
            commands = sql_file.read()
            self._exec_commands(commands)

    def _exec_commands(self, sql):
        """
        Execute all commands in the given file.
        """
        commands = [ c.strip() for c in sql.split(';') ]
        commands = [ c for c in commands if c != '' ]
        try:
            self.conn.execute('begin transaction')
            for c in commands:
                self.conn.execute(c)
            self.conn.execute('commit transaction')
        except Exception as e:
            self.conn.execute('rollback')
            raise e
