-- ref https://www.sqlite.org/lang_altertable.html#otheralter

-- disable foreign key constraint check
PRAGMA foreign_keys=off;

-- start a transaction
BEGIN TRANSACTION;

-- create table new_ with ON DELETE CASCADE for FKs
CREATE TABLE IF NOT EXISTS "new_bookstats" (
	"BkID" INTEGER NOT NULL  ,
	"wordcount" INTEGER NULL  ,
	"distinctterms" INTEGER NULL  ,
	"distinctunknowns" INTEGER NULL  ,
	"unknownpercent" INTEGER NULL  ,
	PRIMARY KEY ("BkID"),
	FOREIGN KEY("BkID") REFERENCES "books" ("BkID") ON UPDATE NO ACTION ON DELETE CASCADE
);

-- delete bad data from the old table
delete from bookstats where BkID not in (select BkID from books);

-- copy data from the table to the new_table
insert into new_bookstats (
BkID,
wordcount,
distinctterms,
distinctunknowns,
unknownpercent
)
select
BkID,
wordcount,
distinctterms,
distinctunknowns,
unknownpercent
from bookstats;

-- drop the old table
DROP TABLE bookstats;

-- rename the new_table to the table
ALTER TABLE new_bookstats RENAME TO bookstats;

-- commit the transaction
COMMIT;

-- re-create indexes and triggers
-- n/a

-- enable foreign key constraint check
PRAGMA foreign_keys=on;
