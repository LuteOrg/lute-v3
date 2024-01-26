-- sqlite only started supporting "alter table drop column" as at v3.35 (I think).
-- for max compatibility with user systems, have to follow process outlined at
-- https://www.sqlitetutorial.net/sqlite-alter-table/

-- disable foreign key constraint check
PRAGMA foreign_keys=off;

-- start a transaction
BEGIN TRANSACTION;

-- Here you can drop column
CREATE TABLE IF NOT EXISTS "new_bookstats" (
	"BkID" INTEGER NOT NULL  ,
	"distinctterms" INTEGER NULL  ,
	"distinctunknowns" INTEGER NULL  ,
	"unknownpercent" INTEGER NULL  ,
        status_distribution VARCHAR(100) NULL,
	PRIMARY KEY ("BkID"),
	FOREIGN KEY("BkID") REFERENCES "books" ("BkID") ON UPDATE NO ACTION ON DELETE CASCADE
);


-- copy data from the table to the new_table
INSERT INTO new_bookstats(
	BkID,
	distinctterms,
	distinctunknowns,
	unknownpercent,
        status_distribution
)
SELECT
	BkID,
	distinctterms,
	distinctunknowns,
	unknownpercent,
        status_distribution
FROM bookstats;

-- drop the table
DROP TABLE bookstats;

-- rename the new_table to the table
ALTER TABLE new_bookstats RENAME TO bookstats;

-- commit the transaction
COMMIT;

-- enable foreign key constraint check
PRAGMA foreign_keys=on;
