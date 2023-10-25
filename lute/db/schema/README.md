# Lute database schema

The baseline schema and migrations for the Lute Sqlite database.

- baseline.sql: the baseline schema and seed data
- migrations: one-time migrations
- migrations_repeatable: repeatable migrations

## How migrations are run

Instead of available migration tools like [Alembic](https://alembic.sqlalchemy.org/en/latest/), Lute uses a simple method of handling database changes which I've been using for many years, and documented [here](https://github.com/jzohrab/DbMigrator/blob/master/docs/managing_database_changes.md).

The migration class `lute.dbsetup.migrator.SqliteMigrator` applies the migrations to the target database, tracking the migrations in the `_migrations` table.

## Creating the baseline

The baseline.sql file is created the development database (data/test_lute.db).  This contains:

* all non-repeatable migrations applied
* demo data

From this project's root dir:

```
# Reset the db to demo state
inv db.reset

# Export and follow the prompts:
inv db.export.baseline

# Double-verify if you want ... then
git add lute/db/schema/baseline.sql
git diff --cached         # verify
git commit -m "Update db baseline.sql"
```

## Creating empty

```
inv db.reset
inv db.export.empty
git add lute/db/schema/empty.sql
git diff --cached    # verify
git commit -m "Update db empty.sql"
```

## Copying over migrations from Lute v2

On a Mac, at least!


```
# Copy the folders over
for f in migrations migrations_repeatable; do cp -r ../lute_dev/db/$f lute/db/schema/; done
git add lute/db/schema/
git diff --cached          # verify
git commit -m "Copy migrations from lute v2."
```