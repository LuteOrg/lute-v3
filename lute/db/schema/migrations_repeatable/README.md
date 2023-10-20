# Repeatable database migrations.

These files should be committed to the repo.

These files get applied on every run of `composer db:migrate`.  They are run *after* all existing pending migrations have been run.