-- ref https://www.sqlite.org/lang_altertable.html#otheralter

-- disable foreign key constraint check
PRAGMA foreign_keys=off;

-- start a transaction
BEGIN TRANSACTION;

-- create same table new_ with ON DELETE CASCADE for FKs
CREATE TABLE "new_booktags" (
	"BtBkID" INTEGER NOT NULL  ,
	"BtT2ID" INTEGER NOT NULL  ,
	PRIMARY KEY ("BtBkID", "BtT2ID"),
	FOREIGN KEY("BtT2ID") REFERENCES "tags2" ("T2ID") ON UPDATE NO ACTION ON DELETE CASCADE,
	FOREIGN KEY("BtBkID") REFERENCES "books" ("BkID") ON UPDATE NO ACTION ON DELETE CASCADE
);

-- delete bad data from the old table
delete from booktags where BtBkID not in (select BkID from books);
delete from booktags where BtT2ID not in (select T2ID from tags2);

-- copy data from the table to the new_table
insert into new_booktags (BtBkID, BtT2ID)
select BtBkID, BtT2ID from booktags;

-- drop the old table
DROP TABLE booktags;

-- rename the new_table to the table
ALTER TABLE new_booktags RENAME TO booktags;

-- commit the transaction
COMMIT;

-- re-create indexes and triggers
CREATE INDEX "BtT2ID" ON "booktags" ("BtT2ID");

-- enable foreign key constraint check
PRAGMA foreign_keys=on;
