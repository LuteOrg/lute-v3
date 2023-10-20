-- Remove excess fields from texts table:

-- ref https://www.sqlite.org/lang_altertable.html
-- 1 Create new table
-- 2 Copy data
-- 3 Drop old table
-- 4 Rename new into old

-- disable foreign key constraint check
PRAGMA foreign_keys=off;

-- start a transaction
BEGIN TRANSACTION;

-- 1. New table, minimal set of fields
CREATE TABLE "new_texts" (
	"TxID" INTEGER NOT NULL  ,
	"TxBkID" INTEGER NOT NULL  ,
	"TxOrder" INTEGER NOT NULL  ,
        "TxText" TEXT NOT NULL  ,
	TxReadDate datetime null,
	PRIMARY KEY ("TxID"),
	FOREIGN KEY("TxBkID") REFERENCES "books" ("BkID") ON UPDATE NO ACTION ON DELETE CASCADE
);

-- 2 Copy data
insert into "new_texts" (
	"TxID",
	"TxBkID",
	"TxOrder",
        "TxText",
	TxReadDate
)
select
	"TxID",
	"TxBkID",
	"TxOrder",
        "TxText",
	TxReadDate
from texts;

-- 3 Drop old table
drop table texts;

-- 4 Rename new into old
ALTER TABLE new_texts RENAME TO texts;

-- commit the transaction
COMMIT;

-- shrink file
VACUUM;

-- enable foreign key constraint check
PRAGMA foreign_keys=on;
