-- ref https://www.sqlite.org/lang_altertable.html#otheralter

-- disable foreign key constraint check
PRAGMA foreign_keys=off;

-- start a transaction
BEGIN TRANSACTION;

-- create same table new_ with ON DELETE CASCADE for FKs
CREATE TABLE "new_wordtags" (
	"WtWoID" INTEGER NOT NULL  ,
	"WtTgID" INTEGER NOT NULL  ,
	PRIMARY KEY ("WtWoID", "WtTgID"),
	FOREIGN KEY("WtWoID") REFERENCES "words" ("WoID") ON UPDATE NO ACTION ON DELETE CASCADE,
	FOREIGN KEY("WtTgID") REFERENCES "tags" ("TgID") ON UPDATE NO ACTION ON DELETE CASCADE
);

-- delete bad data from the old table
delete from wordtags where WtWoID not in (select WoID from words);
delete from wordtags where WtTgID not in (select TgID from tags);

-- copy data from the table to the new_table
insert into new_wordtags (WtWoID, WtTgID)
select WtWoID, WtTgID from wordtags;

-- drop the old table
DROP TABLE wordtags;

-- rename the new_table to the table
ALTER TABLE new_wordtags RENAME TO wordtags;

-- commit the transaction
COMMIT;

-- re-create indexes and triggers
CREATE INDEX "WtTgID" ON "wordtags" ("WtTgID");

-- enable foreign key constraint check
PRAGMA foreign_keys=on;
