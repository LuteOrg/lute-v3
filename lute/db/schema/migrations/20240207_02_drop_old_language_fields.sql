-- sqlite only started supporting "alter table drop column" as at v3.35 (I think).
-- for max compatibility with user systems, have to follow process outlined at
-- https://www.sqlitetutorial.net/sqlite-alter-table/

-- disable foreign key constraint check
PRAGMA foreign_keys=off;

-- start a transaction
BEGIN TRANSACTION;

-- Here you can drop column
CREATE TABLE IF NOT EXISTS "new_languages" (
	"LgID" INTEGER NOT NULL  ,
	"LgName" VARCHAR(40) NOT NULL  ,
	"LgCharacterSubstitutions" VARCHAR(500) NOT NULL  ,
	"LgRegexpSplitSentences" VARCHAR(500) NOT NULL  ,
	"LgExceptionsSplitSentences" VARCHAR(500) NOT NULL  ,
	"LgRegexpWordCharacters" VARCHAR(500) NOT NULL  ,
	"LgRightToLeft" TINYINT NOT NULL  ,
	"LgShowRomanization" TINYINT NOT NULL DEFAULT '0' ,
	"LgParserType" VARCHAR(20) NOT NULL DEFAULT 'spacedel' ,
	PRIMARY KEY ("LgID")
);

-- copy data from the table to the new_table
INSERT INTO new_languages(
	LgID,
	LgName,
	LgCharacterSubstitutions,
	LgRegexpSplitSentences,
	LgExceptionsSplitSentences,
	LgRegexpWordCharacters,
	LgRightToLeft,
	LgShowRomanization,
	LgParserType
)
SELECT
	LgID,
	LgName,
	LgCharacterSubstitutions,
	LgRegexpSplitSentences,
	LgExceptionsSplitSentences,
	LgRegexpWordCharacters,
	LgRightToLeft,
	LgShowRomanization,
	LgParserType
FROM languages;

-- drop the table
DROP TABLE languages;

-- rename the new_table to the table
ALTER TABLE new_languages RENAME TO languages;

-- commit the transaction
COMMIT;

CREATE UNIQUE INDEX "LgName" ON "languages" ("LgName");

-- enable foreign key constraint check
PRAGMA foreign_keys=on;
