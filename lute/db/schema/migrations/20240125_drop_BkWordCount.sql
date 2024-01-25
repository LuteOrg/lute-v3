-- sqlite only started supporting "alter table drop column" as at v3.35 (I think).
-- for max compatibility with user systems, have to follow process outlined at
-- https://www.sqlitetutorial.net/sqlite-alter-table/

-- disable foreign key constraint check
PRAGMA foreign_keys=off;

-- start a transaction
BEGIN TRANSACTION;

-- Here you can drop column
CREATE TABLE IF NOT EXISTS "new_books" (
	"BkID" INTEGER NOT NULL  ,
	"BkLgID" INTEGER NOT NULL  ,
	"BkTitle" VARCHAR(200) NOT NULL  ,
	"BkSourceURI" VARCHAR(1000) NULL  ,
	"BkArchived" TINYINT NOT NULL DEFAULT '0' ,
	"BkCurrentTxID" INTEGER NOT NULL DEFAULT '0',
        BkAudioFilename TEXT NULL,
        BkAudioCurrentPos REAL NULL,
        BkAudioBookmarks TEXT NULL,
	PRIMARY KEY ("BkID"),
	FOREIGN KEY("BkLgID") REFERENCES "languages" ("LgID") ON UPDATE NO ACTION ON DELETE CASCADE
);


-- copy data from the table to the new_table
INSERT INTO new_books(
	BkID,
	BkLgID,
	BkTitle,
	BkSourceURI,
	BkArchived,
	BkCurrentTxID,
        BkAudioFilename,
        BkAudioCurrentPos,
        BkAudioBookmarks
)
SELECT
	BkID,
	BkLgID,
	BkTitle,
	BkSourceURI,
	BkArchived,
	BkCurrentTxID,
        BkAudioFilename,
        BkAudioCurrentPos,
        BkAudioBookmarks
FROM books;

-- drop the table
DROP TABLE books;

-- rename the new_table to the table
ALTER TABLE new_books RENAME TO books;

-- commit the transaction
COMMIT;

CREATE INDEX "BkLgID" ON "books" ("BkLgID");

-- enable foreign key constraint check
PRAGMA foreign_keys=on;
