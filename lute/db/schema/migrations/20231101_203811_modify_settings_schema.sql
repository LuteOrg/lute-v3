-- Change settings table

-- ref https://www.sqlite.org/lang_altertable.html
-- 1 Create new table
-- 2 Copy data
-- 3 Drop old table
-- 4 Rename new into old

-- disable foreign key constraint check
PRAGMA foreign_keys=off;

-- start a transaction
BEGIN TRANSACTION;

-- 1. New table

CREATE TABLE "new_settings" (
	"StKey" VARCHAR(40) NOT NULL,
        "StKeyType" TEXT NOT NULL,
	"StValue" TEXT NULL,
	PRIMARY KEY ("StKey")
);

-- 2 Copy data
insert into new_settings (StKey, StKeyType, StValue)
select
StKey, 'system', StValue from settings;

-- fix:
update new_settings
set StKeyType = 'user'
where StKey in ('backup_enabled', 'backup_auto', 'backup_warn', 'backup_dir', 'backup_count');

-- 3 Drop old table
drop table settings;

-- 4 Rename new into old
ALTER TABLE new_settings RENAME TO settings;

-- commit the transaction
COMMIT;

-- shrink file
VACUUM;

-- enable foreign key constraint check
PRAGMA foreign_keys=on;

