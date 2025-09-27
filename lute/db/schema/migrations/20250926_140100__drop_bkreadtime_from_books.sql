PRAGMA foreign_keys=off;

BEGIN TRANSACTION;

CREATE TABLE books_new (
    BkID INTEGER NOT NULL,
    BkLgID INTEGER NOT NULL,
    BkTitle VARCHAR(200) NOT NULL,
    BkSourceURI VARCHAR(1000),
    BkArchived TINYINT NOT NULL DEFAULT 0,
    BkCurrentTxID INTEGER NOT NULL DEFAULT 0,
    BkAudioFilename TEXT,
    BkAudioCurrentPos REAL,
    BkAudioBookmarks TEXT,
    PRIMARY KEY (BkID),
    FOREIGN KEY(BkLgID) REFERENCES languages (LgID) ON DELETE CASCADE
);

INSERT INTO books_new (BkID, BkLgID, BkTitle, BkSourceURI, BkArchived, BkCurrentTxID, BkAudioFilename, BkAudioCurrentPos, BkAudioBookmarks)
SELECT BkID, BkLgID, BkTitle, BkSourceURI, BkArchived, BkCurrentTxID, BkAudioFilename, BkAudioCurrentPos, BkAudioBookmarks FROM books;

DROP TABLE books;

ALTER TABLE books_new RENAME TO books;

COMMIT;

PRAGMA foreign_keys=on;
