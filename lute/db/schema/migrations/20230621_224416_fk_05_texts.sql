-- ref https://www.sqlite.org/lang_altertable.html#otheralter

-- disable foreign key constraint check
PRAGMA foreign_keys=off;

-- start a transaction
BEGIN TRANSACTION;

-- create table new_ with ON DELETE CASCADE for FKs
CREATE TABLE new_texts (
	"TxID" INTEGER NOT NULL  ,
	"TxBkID" INTEGER NOT NULL  ,
	"TxOrder" INTEGER NOT NULL  ,
	"TxLgID" INTEGER NOT NULL  ,
	"TxTitle" VARCHAR(200) NOT NULL  ,
	"TxText" TEXT NOT NULL  ,
	"TxAudioURI" VARCHAR(200) NULL  ,
	"TxSourceURI" VARCHAR(1000) NULL  ,
	"TxArchived" TINYINT NOT NULL DEFAULT '0' , TxReadDate datetime null,
	PRIMARY KEY ("TxID"),
	FOREIGN KEY("TxBkID") REFERENCES "books" ("BkID") ON UPDATE NO ACTION ON DELETE CASCADE,
	FOREIGN KEY("TxLgID") REFERENCES "languages" ("LgID") ON UPDATE NO ACTION ON DELETE CASCADE
);

-- delete bad data from the old table
delete from texts where TxBkID not in (select BkID from books);
delete from texts where TxLgID not in (select LgID from languages);

-- copy data from the table to the new_table
insert into new_texts (
TxID,
TxBkID,
TxOrder,
TxLgID,
TxTitle,
TxText,
TxAudioURI,
TxSourceURI,
TxArchived,
TxReadDate
)
select
TxID,
TxBkID,
TxOrder,
TxLgID,
TxTitle,
TxText,
TxAudioURI,
TxSourceURI,
TxArchived,
TxReadDate
from texts;

-- drop the old table
DROP TABLE texts;

-- rename the new_table to the table
ALTER TABLE new_texts RENAME TO texts;

-- commit the transaction
COMMIT;

-- re-create indexes and triggers
CREATE UNIQUE INDEX "TxBkIDTxOrder" ON "texts" ("TxBkID", "TxOrder");

-- enable foreign key constraint check
PRAGMA foreign_keys=on;
