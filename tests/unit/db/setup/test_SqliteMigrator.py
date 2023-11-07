"""
DB migration tests.
"""

import sqlite3
from contextlib import closing
import pytest

from lute.db.setup.migrator import SqliteMigrator


@pytest.fixture(name="db")
def fixture_db(tmp_path):
    """
    Create a db for migrations, return the connection.
    """
    dbfile = tmp_path / "test.db"

    sql = """
    create table A (a int);

    CREATE TABLE IF NOT EXISTS "_migrations" (
	"filename" VARCHAR(255) NOT NULL  ,
	PRIMARY KEY ("filename")
    );
    """
    with closing(sqlite3.connect(dbfile)) as conn:
        conn.executescript(sql)
        yield conn


@pytest.fixture(name="migdirs")
def fixture_migdirs(tmp_path):
    """
    Create folders for migration files.
    """
    migs = tmp_path / "migrations"
    migs.mkdir()
    reps = tmp_path / "repeatable"
    reps.mkdir()
    return tmp_path


def test_no_migrations(db, migdirs):
    """
    No migrations if no unapplied files yet.
    """
    migrator = SqliteMigrator(migdirs / "migrations", migdirs / "repeatable")
    assert migrator.has_migrations(db) is False, "no migrations"

    migfile = migdirs / "migrations" / "a.sql"
    migfile.write_text("create table B (b int);")
    assert migrator.has_migrations(db) is True, "have migrations"


def test_migration_applied(db, migdirs):
    """
    Migrations are applied, and tracked.
    """
    migrator = SqliteMigrator(migdirs / "migrations", migdirs / "repeatable")

    migfile = migdirs / "migrations" / "b.sql"
    migfile.write_text("create table B (b int);")
    assert migrator.has_migrations(db) is True, "have migrations"

    migrator.do_migration(db)

    assert migrator.has_migrations(db) is False, "no outstanding migrations"

    cur = db.cursor()
    sql = """SELECT name FROM sqlite_master
    WHERE type='table' AND name in ('A', 'B')
    order by name;"""
    tnames = cur.execute(sql).fetchall()
    tnames = [t[0] for t in tnames]
    assert tnames == ["A", "B"], "migrations run"


def test_bad_migration_throws(db, migdirs):
    """
    Bad migration throws.
    """
    migrator = SqliteMigrator(migdirs / "migrations", migdirs / "repeatable")

    migfile = migdirs / "migrations" / "b.sql"
    migfile.write_text("create tableXXXX B (b int);")
    assert migrator.has_migrations(db) is True, "have migrations"

    with pytest.raises(sqlite3.OperationalError):
        migrator.do_migration(db)

    assert migrator.has_migrations(db), "bad file still pending!!!"


def test_repeatable_migs_are_always_applied(db, migdirs):
    """
    Always applied, even if no migrations.
    """
    migrator = SqliteMigrator(migdirs / "migrations", migdirs / "repeatable")

    migfile = migdirs / "repeatable" / "r.sql"
    migfile.write_text("drop view if exists v1; create view v1 as select 1;")
    assert migrator.has_migrations(db) is False, "have migrations"
    migrator.do_migration(db)

    cur = db.cursor()
    vals = cur.execute("SELECT * from v1;").fetchall()
    assert vals == [(1,)], "migrations run"

    migfile = migdirs / "repeatable" / "r.sql"
    migfile.write_text("drop view if exists v1; create view v1 as select 2;")
    assert migrator.has_migrations(db) is False, "have migrations"
    migrator.do_migration(db)

    cur = db.cursor()
    vals = cur.execute("SELECT * from v1;").fetchall()
    assert vals == [(2,)], "changed"


def test_bad_repeatable_migs_throws(db, migdirs):
    """
    Bad repeatable should throw.
    """
    migrator = SqliteMigrator(migdirs / "migrations", migdirs / "repeatable")
    migfile = migdirs / "repeatable" / "r.sql"
    migfile.write_text("drop view if exists v1; create blahblah")

    with pytest.raises(sqlite3.OperationalError):
        migrator.do_migration(db)
