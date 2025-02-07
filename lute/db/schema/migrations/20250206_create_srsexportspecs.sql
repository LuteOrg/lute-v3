-- srs export specs

CREATE TABLE IF NOT EXISTS "srsexportspecs" (
       "SrsID" INTEGER NOT NULL,
       "SrsExportName" VARCHAR(200) NOT NULL UNIQUE,
       "SrsCriteria" VARCHAR(1000) NOT NULL,
       "SrsDeckName" VARCHAR(200) NOT NULL,
       "SrsNoteType" VARCHAR(200) NOT NULL,       
       "SrsFieldMapping" VARCHAR(1000) NOT NULL,
       "SrsActive" TINYINT NOT NULL DEFAULT '1',
       PRIMARY KEY ("SrsID")
);
