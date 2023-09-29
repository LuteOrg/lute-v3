-- ref https://www.sqlite.org/lang_altertable.html#otheralter

-- disable foreign key constraint check
PRAGMA foreign_keys=off;

-- start a transaction
BEGIN TRANSACTION;

-- create table new_ with ON DELETE CASCADE for FKs
CREATE TABLE IF NOT EXISTS "new_wordparents" (
	"WpWoID" INTEGER NOT NULL  ,
	"WpParentWoID" INTEGER NOT NULL  ,
	PRIMARY KEY ("WpWoID"),
	FOREIGN KEY("WpParentWoID") REFERENCES "words" ("WoID") ON UPDATE NO ACTION ON DELETE CASCADE,
	FOREIGN KEY("WpWoID") REFERENCES "words" ("WoID") ON UPDATE NO ACTION ON DELETE CASCADE
);

-- delete bad data from the old table
delete from wordparents where WpWoID not in (select WoID from words);
delete from wordparents where WpParentWoID not in (select WoID from words);

-- copy data from the table to the new_table
insert into new_wordparents (
WpWoID, WpParentWoID
)
select
WpWoID, WpParentWoID
from wordparents;

-- drop the old table
DROP TABLE wordparents;

-- rename the new_table to the table
ALTER TABLE new_wordparents RENAME TO wordparents;

-- commit the transaction
COMMIT;

-- re-create indexes and triggers
CREATE INDEX "WpParentWoID" ON "wordparents" ("WpParentWoID");

-- enable foreign key constraint check
PRAGMA foreign_keys=on;
