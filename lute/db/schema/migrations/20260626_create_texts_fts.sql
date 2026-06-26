-- Create content View for FTS5
CREATE VIEW IF NOT EXISTS v_texts_content AS
SELECT t.TxID AS rowid, b.BkTitle, t.TxText
FROM texts t
JOIN books b ON b.BkID = t.TxBkID;

-- Create FTS5 virtual table using the external content view
CREATE VIRTUAL TABLE IF NOT EXISTS texts_fts USING fts5(
    BkTitle,
    TxText,
    content='v_texts_content'
);

-- Populate the FTS index
INSERT INTO texts_fts(rowid, BkTitle, TxText)
SELECT t.TxID, b.BkTitle, t.TxText
FROM texts t
JOIN books b ON b.BkID = t.TxBkID;
