-- ref https://www.sqlite.org/lang_altertable.html#otheralter

-- disable foreign key constraint check
PRAGMA foreign_keys=off;

-- start a transaction
BEGIN TRANSACTION;

-- create table new_ with ON DELETE CASCADE for FKs
CREATE TABLE "new_texttokens" (
	"TokTxID" INTEGER NOT NULL  ,
	"TokSentenceNumber" MEDIUMINT NOT NULL  ,
	"TokOrder" SMALLINT NOT NULL  ,
	"TokIsWord" TINYINT NOT NULL  ,
	"TokText" VARCHAR(100) NOT NULL  , TokTextLC VARCHAR(100) NOT NULL,
	PRIMARY KEY ("TokTxID", "TokOrder"),
	FOREIGN KEY("TokTxID") REFERENCES "texts" ("TxID") ON UPDATE NO ACTION ON DELETE CASCADE
);

-- delete bad data from the old table
delete from texttokens where TokTxID not in (select TxID from texts);

-- copy data from the table to the new_table
insert into new_texttokens (TokTxID, TokSentenceNumber, TokOrder, TokIsWord, TokText, TokTextLC)
select TokTxID, TokSentenceNumber, TokOrder, TokIsWord, TokText, TokTextLC from texttokens;

-- drop the old table
DROP TABLE texttokens;

-- rename the new_table to the table
ALTER TABLE new_texttokens RENAME TO texttokens;

-- commit the transaction
COMMIT;

-- re-create indexes and triggers
-- n/a

-- enable foreign key constraint check
PRAGMA foreign_keys=on;
