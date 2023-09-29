-- ref https://www.sqlite.org/lang_altertable.html#otheralter

-- disable foreign key constraint check
PRAGMA foreign_keys=off;

-- start a transaction
BEGIN TRANSACTION;

-- create table new_ with ON DELETE CASCADE for FKs
CREATE TABLE new_wordflashmessages (
  "WfID" INTEGER NOT NULL,
  "WfWoID" INTEGER NOT NULL,
  "WfMessage" VARCHAR(200) NOT NULL,
  PRIMARY KEY ("WfID"),
  FOREIGN KEY("WfWoID") REFERENCES "words" ("WoID") ON UPDATE NO ACTION ON DELETE CASCADE
);

-- delete bad data from the old table
delete from wordflashmessages where WfWoID not in (select WoID from words);

-- copy data from the table to the new_table
insert into new_wordflashmessages (
WfID,
WfWoID,
WfMessage
)
select
WfID,
WfWoID,
WfMessage
from wordflashmessages;

-- drop the old table
DROP TABLE wordflashmessages;

-- rename the new_table to the table
ALTER TABLE new_wordflashmessages RENAME TO wordflashmessages;

-- commit the transaction
COMMIT;

-- re-create indexes and triggers
-- n/a

-- enable foreign key constraint check
PRAGMA foreign_keys=on;
