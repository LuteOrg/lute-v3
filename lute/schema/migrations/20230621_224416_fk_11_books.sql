-- ref https://www.sqlite.org/lang_altertable.html#otheralter

-- disable foreign key constraint check
PRAGMA foreign_keys=off;

-- start a transaction
BEGIN TRANSACTION;

-- create table new_ with ON DELETE CASCADE for FKs
CREATE TABLE IF NOT EXISTS "new_books" (
	"BkID" INTEGER NOT NULL  ,
	"BkLgID" INTEGER NOT NULL  ,
	"BkTitle" VARCHAR(200) NOT NULL  ,
	"BkSourceURI" VARCHAR(1000) NULL  ,
	"BkArchived" TINYINT NOT NULL DEFAULT '0' ,
	"BkCurrentTxID" INTEGER NOT NULL DEFAULT '0' ,
	PRIMARY KEY ("BkID"),
	FOREIGN KEY("BkLgID") REFERENCES "languages" ("LgID") ON UPDATE NO ACTION ON DELETE CASCADE
);

-- delete bad data from the old table
delete from books where BkLgID not in (select LgID from languages);

-- copy data from the table to the new_table
insert into new_books (
BkID,
BkLgID,
BkTitle,
BkSourceURI,
BkArchived,
BkCurrentTxID
)
select
BkID,
BkLgID,
BkTitle,
BkSourceURI,
BkArchived,
BkCurrentTxID
from books;

-- drop the old table
DROP TABLE books;

-- rename the new_table to the table
ALTER TABLE new_books RENAME TO books;

-- commit the transaction
COMMIT;

-- re-create indexes and triggers
CREATE INDEX "BkLgID" ON "books" ("BkLgID");

-- enable foreign key constraint check
PRAGMA foreign_keys=on;
