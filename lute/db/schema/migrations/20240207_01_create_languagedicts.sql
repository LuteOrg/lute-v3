-- Language dict table

CREATE TABLE languagedicts (
  "LdID" INTEGER NOT NULL,
  "LdLgID" INTEGER NOT NULL,
  "LdUseFor" VARCHAR(20) NOT NULL,
  "LdType" VARCHAR(20) NOT NULL,
  "LdDictURI" VARCHAR(200) NOT NULL,
  "LdIsActive" TINYINT NOT NULL DEFAULT 1,
  "LdSortOrder" INTEGER NOT NULL,
  PRIMARY KEY ("LdID"),
  FOREIGN KEY("LdLgID") REFERENCES "languages" ("LgID") ON UPDATE NO ACTION ON DELETE CASCADE
);


-- Copy existing dictionary data to new table.

-- TERMS: dict 1

-- embedded
insert into languagedicts (LdLgID, LdUseFor, LdType, LdDictURI, LdSortOrder)
select lgid, "terms", "embeddedhtml", LgDict1URI, 1
from languages where LgDict1URI is not null and LgDict1URI NOT LIKE '*%';

-- popup
insert into languagedicts (LdLgID, LdUseFor, LdType, LdDictURI, LdSortOrder)
select lgid, "terms", "popuphtml", substr(LgDict1URI,2), 2
from languages where LgDict1URI is not null and LgDict1URI LIKE '*%';


-- TERMS: dict 2

-- embedded
insert into languagedicts (LdLgID, LdUseFor, LdType, LdDictURI, LdSortOrder)
select lgid, "terms", "embeddedhtml", LgDict2URI, 2
from languages where LgDict2URI is not null and LgDict2URI NOT LIKE '*%';

-- popup
insert into languagedicts (LdLgID, LdUseFor, LdType, LdDictURI, LdSortOrder)
select lgid, "terms", "popuphtml", substr(LgDict2URI,2), 2
from languages where LgDict2URI is not null and LgDict2URI LIKE '*%';


-- SENTENCES

-- embedded
insert into languagedicts (LdLgID, LdUseFor, LdType, LdDictURI, LdSortOrder)
select lgid, "sentences", "embeddedhtml", LgGoogleTranslateURI, 3
from languages where LgGoogleTranslateURI is not null and LgGoogleTranslateURI NOT LIKE '*%';

-- popup
insert into languagedicts (LdLgID, LdUseFor, LdType, LdDictURI, LdSortOrder)
select lgid, "sentences", "popuphtml", substr(LgGoogleTranslateURI,2), 3
from languages where LgGoogleTranslateURI is not null and LgGoogleTranslateURI LIKE '*%';
