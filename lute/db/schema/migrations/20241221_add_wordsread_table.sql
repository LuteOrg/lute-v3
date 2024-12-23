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
insert into wordsread (WrLgID, WrTxID, WrReadDate, WrWordCount)
select bklgid, txid, txreaddate, txwordcount from texts inner join books on bkid=txbkid where txreaddate is not null;
