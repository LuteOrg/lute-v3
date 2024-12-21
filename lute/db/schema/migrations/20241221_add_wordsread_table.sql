CREATE TABLE IF NOT EXISTS "wordsread" (
	"WrID" INTEGER NOT NULL,
        "WrLgID" INTEGER NOT NULL,
	"WrTxID" INTEGER NULL,
        "WrReadDate" DATETIME NOT NULL,
        "WrWordCount" INTEGER NOT NULL,
	PRIMARY KEY ("WrID"),
        FOREIGN KEY("WrTxID") REFERENCES "texts" ("TxID") ON DELETE SET NULL,
        FOREIGN KEY("WrLgID") REFERENCES "languages" ("LgID") ON UPDATE NO ACTION ON DELETE CASCADE
);

-- load initial data.
insert into wordsread (WrTxID, WrReadDate, WrWordCount)
select txid, txreaddate, txwordcount from texts where txreaddate is not null;
