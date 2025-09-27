CREATE TABLE reading_tracking (
    id INTEGER PRIMARY KEY,
    book_id INTEGER NOT NULL,
    read_date DATETIME NOT NULL,
    duration_seconds INTEGER NOT NULL,
    FOREIGN KEY (book_id) REFERENCES books(BkID) ON DELETE CASCADE
);
