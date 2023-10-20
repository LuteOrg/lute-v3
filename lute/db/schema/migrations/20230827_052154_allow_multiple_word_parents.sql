-- https://www.sqlitetutorial.net/sqlite-alter-table/

-- disable foreign key constraint check
PRAGMA foreign_keys=off;

BEGIN TRANSACTION;

CREATE TABLE IF NOT EXISTS "new_wordparents" (
	"WpWoID" INTEGER NOT NULL  ,
	"WpParentWoID" INTEGER NOT NULL  ,
	FOREIGN KEY("WpParentWoID") REFERENCES "words" ("WoID") ON UPDATE NO ACTION ON DELETE CASCADE,
	FOREIGN KEY("WpWoID") REFERENCES "words" ("WoID") ON UPDATE NO ACTION ON DELETE CASCADE
);

INSERT INTO new_wordparents(
WpWoID, WpParentWoID
)
SELECT
WpWoID, WpParentWoID
FROM wordparents;

DROP TABLE wordparents;

ALTER TABLE new_wordparents RENAME TO wordparents;

COMMIT;

CREATE UNIQUE INDEX "wordparent_pair" ON "wordparents" ("WpWoID", "WpParentWoID");

PRAGMA foreign_keys=on;
