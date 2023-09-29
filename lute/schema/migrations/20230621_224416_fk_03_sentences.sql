-- ref https://www.sqlite.org/lang_altertable.html#otheralter

-- disable foreign key constraint check
PRAGMA foreign_keys=off;

-- start a transaction
BEGIN TRANSACTION;

-- create table new_ with ON DELETE CASCADE for FKs
-- note dropping some fields
CREATE TABLE IF NOT EXISTS "new_sentences" (
	"SeID" INTEGER NOT NULL  ,
	"SeTxID" INTEGER NOT NULL  ,
	"SeOrder" SMALLINT NOT NULL  ,
	"SeText" TEXT NULL  ,
	PRIMARY KEY ("SeID"),
	FOREIGN KEY("SeTxID") REFERENCES "texts" ("TxID") ON UPDATE NO ACTION ON DELETE CASCADE
);

-- delete bad data from the old table
delete from sentences where SeLgID not in (select LgID from languages);
delete from sentences where SeTxID not in (select TxID from texts);

-- copy data from the table to the new_table
insert into new_sentences (SeID, SeTxID, SeOrder, SeText)
select SeID, SeTxID, SeOrder, SeText from sentences;

-- drop the old table
DROP TABLE sentences;

-- rename the new_table to the table
ALTER TABLE new_sentences RENAME TO sentences;

-- commit the transaction
COMMIT;

-- re-create indexes and triggers
CREATE INDEX "SeOrder" ON "sentences" ("SeOrder");
CREATE INDEX "SeTxID" ON "sentences" ("SeTxID");

-- enable foreign key constraint check
PRAGMA foreign_keys=on;
