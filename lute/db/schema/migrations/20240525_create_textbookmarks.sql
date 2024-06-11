-- https://www.sqlitetutorial.net/sqlite-alter-table/

BEGIN TRANSACTION;

PRAGMA foreign_keys=on;

-- Text bookmarks table
CREATE TABLE textbookmarks (
  "TbID" INTEGER PRIMARY KEY,
  "TbTxID" INTEGER NOT NULL,
  "TbTitle" VARCHAR(200) NOT NULL,
  FOREIGN KEY("TbTxID") REFERENCES "texts" ("TxID") ON DELETE CASCADE
);

PRAGMA foreign_keys=off;

COMMIT;