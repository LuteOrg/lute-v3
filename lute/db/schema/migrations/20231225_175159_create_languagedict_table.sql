-- Language dict table

CREATE TABLE languagedicts (
  "LdID" INTEGER NOT NULL,
  "LdLgID" INTEGER NOT NULL,
  "LdType" VARCHAR(20) NOT NULL,
  "LdDictURI" VARCHAR(200) NOT NULL,
  "LdSortOrder" INTEGER NOT NULL,
  PRIMARY KEY ("LdID"),
  FOREIGN KEY("LdLgID") REFERENCES "languages" ("LgID") ON UPDATE NO ACTION ON DELETE CASCADE
);


-- Copy existing dictionary data to new table.

-- dict 1

-- embedded
insert into languagedicts (LdLgID, LdType, LdDictURI, LdSortOrder)
select lgid, "embeddedhtml", LgDict1URI, 1
from languages where LgDict1URI is not null and LgDict1URI NOT LIKE '*%';

-- popup
insert into languagedicts (LdLgID, LdType, LdDictURI, LdSortOrder)
select lgid, "popuphtml", substr(LgDict1URI,2), 2
from languages where LgDict1URI is not null and LgDict1URI LIKE '*%';


-- dict 2

-- embedded
insert into languagedicts (LdLgID, LdType, LdDictURI, LdSortOrder)
select lgid, "embeddedhtml", LgDict2URI, 2
from languages where LgDict2URI is not null and LgDict2URI NOT LIKE '*%';

-- popup
insert into languagedicts (LdLgID, LdType, LdDictURI, LdSortOrder)
select lgid, "popuphtml", substr(LgDict2URI,2), 2
from languages where LgDict2URI is not null and LgDict2URI LIKE '*%';


-- TODO -- have to check if starts w/ * or not, like the above.
-- update languages
-- set LgGoogleTranslateURI = substr(LgGoogleTranslateURI, 2)
-- where LgGoogleTranslateURI is not null and LgGoogleTranslateURI LIKE '*%';
