-- sqlite only started supporting "alter table drop column" as at v3.35 (I think).
-- for max compatibility with user systems, have to follow process outlined at
-- https://www.sqlitetutorial.net/sqlite-alter-table/

-- disable foreign key constraint check
PRAGMA foreign_keys=off;

-- start a transaction
BEGIN TRANSACTION;

-- Here you can drop column
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
	FOREIGN KEY("WoLgID") REFERENCES "languages" ("LgID") ON UPDATE NO ACTION ON DELETE NO ACTION
);

-- copy data from the table to the new_table
INSERT INTO new_words(
	"WoID",
	"WoLgID",
	"WoText",
	"WoTextLC",
	"WoStatus",
	"WoTranslation",
	"WoRomanization",
	"WoTokenCount",
	"WoCreated",
	"WoStatusChanged"
)
SELECT
	"WoID",
	"WoLgID",
	"WoText",
	"WoTextLC",
	"WoStatus",
	"WoTranslation",
	"WoRomanization",
	"WoTokenCount",
	"WoCreated",
	"WoStatusChanged"
FROM words;

-- drop the table
DROP TABLE words;

-- rename the new_table to the table
ALTER TABLE new_words RENAME TO words;

-- commit the transaction
COMMIT;

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
