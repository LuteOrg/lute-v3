DROP TRIGGER IF EXISTS trig_words_update_WoStatusChanged;

CREATE TRIGGER trig_words_update_WoStatusChanged
AFTER UPDATE OF WoStatus ON words
FOR EACH ROW
WHEN old.WoStatus <> new.WoStatus
BEGIN
    UPDATE words
    SET WoStatusChanged = CURRENT_TIMESTAMP
    WHERE WoID = NEW.WoID;
END;
