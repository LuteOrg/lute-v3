DROP TRIGGER IF EXISTS trig_wordparents_after_insert_update_parent_WoStatus_if_following;

CREATE TRIGGER trig_wordparents_after_insert_update_parent_WoStatus_if_following
-- created by db/schema/migrations_repeatable/trig_wordparents.sql
AFTER INSERT ON wordparents
BEGIN
    UPDATE words
    SET WoStatus = (
      select WoStatus from words where WoID = new.WpWoID
    )
    WHERE WoID = new.WpParentWoID
    AND 1 = (
      SELECT COUNT(*)
      FROM wordparents
      INNER JOIN words ON WoID = WpWoID
      WHERE WoSyncStatus = 1
      AND WoID = new.WpWoID
    );
END;


DROP TRIGGER IF EXISTS trig_wordparents_after_delete_change_WoSyncStatus;

CREATE TRIGGER trig_wordparents_after_delete_change_WoSyncStatus
-- created by db/schema/migrations_repeatable/trig_wordparents.sql
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
