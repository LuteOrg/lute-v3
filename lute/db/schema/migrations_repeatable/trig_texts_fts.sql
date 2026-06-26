-- Repeatable triggers to keep texts_fts external index synchronized with books and texts.

DROP TRIGGER IF EXISTS trig_texts_after_insert_update_fts;
CREATE TRIGGER trig_texts_after_insert_update_fts
AFTER INSERT ON texts
BEGIN
    INSERT INTO texts_fts(rowid, BkTitle, TxText)
    SELECT new.TxID, b.BkTitle, new.TxText
    FROM books b
    WHERE b.BkID = new.TxBkID;
END;

DROP TRIGGER IF EXISTS trig_texts_after_delete_update_fts;
CREATE TRIGGER trig_texts_after_delete_update_fts
AFTER DELETE ON texts
BEGIN
    INSERT INTO texts_fts(texts_fts, rowid, BkTitle, TxText)
    SELECT 'delete', old.TxID, b.BkTitle, old.TxText
    FROM books b
    WHERE b.BkID = old.TxBkID;
END;

DROP TRIGGER IF EXISTS trig_texts_after_update_text_update_fts;
CREATE TRIGGER trig_texts_after_update_text_update_fts
AFTER UPDATE OF TxText ON texts
BEGIN
    -- De-index old content
    INSERT INTO texts_fts(texts_fts, rowid, BkTitle, TxText)
    SELECT 'delete', old.TxID, b.BkTitle, old.TxText
    FROM books b
    WHERE b.BkID = old.TxBkID;
    
    -- Index new content
    INSERT INTO texts_fts(rowid, BkTitle, TxText)
    SELECT new.TxID, b.BkTitle, new.TxText
    FROM books b
    WHERE b.BkID = new.TxBkID;
END;

DROP TRIGGER IF EXISTS trig_books_after_update_title_update_fts;
CREATE TRIGGER trig_books_after_update_title_update_fts
AFTER UPDATE OF BkTitle ON books
BEGIN
    -- De-index all old titles for this book's texts
    INSERT INTO texts_fts(texts_fts, rowid, BkTitle, TxText)
    SELECT 'delete', t.TxID, old.BkTitle, t.TxText
    FROM texts t
    WHERE t.TxBkID = new.BkID;
    
    -- Index all new titles for this book's texts
    INSERT INTO texts_fts(rowid, BkTitle, TxText)
    SELECT t.TxID, new.BkTitle, t.TxText
    FROM texts t
    WHERE t.TxBkID = new.BkID;
END;
