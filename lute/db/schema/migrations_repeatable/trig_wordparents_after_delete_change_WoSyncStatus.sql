DROP TRIGGER IF EXISTS trig_wordparents_after_delete_change_WoSyncStatus;

CREATE TRIGGER trig_wordparents_after_delete_change_WoSyncStatus
BEFORE DELETE ON wordparents
FOR EACH ROW
BEGIN
    UPDATE words
    SET WoSyncStatus = 0
    WHERE WoID IN
    (
      select WpWoID from wordparents
      where WpParentWoID = old.WpParentWoID
    );
END;
