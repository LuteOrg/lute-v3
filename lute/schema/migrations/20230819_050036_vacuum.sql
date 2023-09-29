-- have deleted the textitems table from the db,
-- but need to vacuum the db to reclaim the lost file space.
-- https://www.sqlitetutorial.net/sqlite-vacuum/

vacuum;
