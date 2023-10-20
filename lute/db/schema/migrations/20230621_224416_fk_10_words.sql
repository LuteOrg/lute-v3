-- ref https://www.sqlite.org/lang_altertable.html#otheralter

-- disable foreign key constraint check
PRAGMA foreign_keys=off;

-- start a transaction
BEGIN TRANSACTION;

-- create table new_ with ON DELETE CASCADE for FKs
CREATE TABLE IF NOT EXISTS "new_words" (
	"WoID" INTEGER NOT NULL PRIMARY KEY ,
	"WoLgID" INTEGER NOT NULL  ,
	"WoText" VARCHAR(250) NOT NULL  ,
	"WoTextLC" VARCHAR(250) NOT NULL  ,
	"WoStatus" TINYINT NOT NULL  ,
	"WoTranslation" VARCHAR(500) NULL  ,
	"WoRomanization" VARCHAR(100) NULL  ,
	"WoTokenCount" TINYINT NOT NULL DEFAULT '0' ,
	"WoCreated" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ,
	"WoStatusChanged" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY("WoLgID") REFERENCES "languages" ("LgID") ON UPDATE NO ACTION ON DELETE CASCADE
);

-- delete bad data from the old table
delete from words where WoLgID not in (select LgID from languages);

-- copy data from the table to the new_table
insert into new_words (
WoID,
WoLgID,
WoText,
WoTextLC,
WoStatus,
WoTranslation,
WoRomanization,
WoTokenCount,
WoCreated,
WoStatusChanged
)
select
WoID,
WoLgID,
WoText,
WoTextLC,
WoStatus,
WoTranslation,
WoRomanization,
WoTokenCount,
WoCreated,
WoStatusChanged
from words;

-- drop the old table
DROP TABLE words;

-- rename the new_table to the table
ALTER TABLE new_words RENAME TO words;

-- commit the transaction
COMMIT;

-- re-create indexes and triggers
CREATE INDEX "WoLgID" ON "words" ("WoLgID");
CREATE INDEX "WoStatus" ON "words" ("WoStatus");
CREATE INDEX "WoStatusChanged" ON "words" ("WoStatusChanged");
CREATE INDEX "WoTextLC" ON "words" ("WoTextLC");
CREATE UNIQUE INDEX "WoTextLCLgID" ON "words" ("WoTextLC", "WoLgID");
CREATE INDEX "WoTokenCount" ON "words" ("WoTokenCount");
CREATE TRIGGER trig_words_update_WoStatusChanged
AFTER UPDATE OF WoStatus ON words
FOR EACH ROW
WHEN old.WoStatus <> new.WoStatus
BEGIN
    UPDATE words
    SET WoStatusChanged = CURRENT_TIMESTAMP
    WHERE WoID = NEW.WoID;
END;


-- enable foreign key constraint check
PRAGMA foreign_keys=on;
