-- ref https://www.sqlite.org/lang_altertable.html#otheralter

-- disable foreign key constraint check
PRAGMA foreign_keys=off;

-- start a transaction
BEGIN TRANSACTION;

-- create table new_ with ON DELETE CASCADE for FKs
CREATE TABLE "new_wordimages" (
	"WiID" INTEGER NOT NULL  ,
	"WiWoID" INTEGER NOT NULL  ,
	"WiSource" VARCHAR(500) NOT NULL  ,
	PRIMARY KEY ("WiID"),
	FOREIGN KEY("WiWoID") REFERENCES "words" ("WoID") ON UPDATE NO ACTION ON DELETE CASCADE
);

-- delete bad data from the old table
delete from wordimages where WiWoID not in (select WoID from words);

-- copy data from the table to the new_table
insert into new_wordimages (
WiID,
WiWoID,
WiSource
)
select
WiID,
WiWoID,
WiSource
from wordimages;

-- drop the old table
DROP TABLE wordimages;

-- rename the new_table to the table
ALTER TABLE new_wordimages RENAME TO wordimages;

-- commit the transaction
COMMIT;

-- re-create indexes and triggers
CREATE INDEX "WiWoID" ON "wordimages" ("WiWoID");

-- enable foreign key constraint check
PRAGMA foreign_keys=on;
