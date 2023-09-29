# Lute database schema

The baseline schema and migrations for the Lute Sqlite database.

- baseline.sql: the baseline schema and seed data
- migrations: one-time migrations
- migrations_repeatable: repeatable migrations

## How migrations are run

Instead of available migration tools like [Alembic](https://alembic.sqlalchemy.org/en/latest/), Lute uses a simple method of handling database changes which I've been using for many years, and documented [here](https://github.com/jzohrab/DbMigrator/blob/master/docs/managing_database_changes.md).

The migration class `lute.dbsetup.migrator.SqliteMigrator` applies the migrations to the target database, tracking the migrations in the `_migrations` table.

## Creating the baseline

As of now (late 2023), the baseline.sql file is created from the latest `develop` branch in Lute v2, that is Lute running in PHP:

From this project's root dir:

```
# Check the current branch, and reset the db:
pushd ../lute_dev
git st                    # should be clean!
git checkout develop      # should be develop!
composer dev:data:load    # set to baseline!
popd

sqlite3 ../lute_dev/data/test_lute.db .dump > lute/schema/baseline.sql
git add lute/schema/baseline.sql
git diff --cached         # verify
git commit -m "Update db baseline.sql"
```

## Copying over migrations from Lute v2

On a Mac, at least!


```
# Copy the folders over
for f in migrations migrations_repeatable; do cp -r ../lute_dev/db/$f lute/schema/; done

git add lute/schema/migrations/
git add lute/schema/migrations_repeatable/
git diff --cached          # verify
git commit -m "Copy migrations from lute v2."
```