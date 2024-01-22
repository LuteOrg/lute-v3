DROP TRIGGER IF EXISTS trig_wordparents_after_insert_update_parent_WoStatus_if_following;

CREATE TRIGGER trig_wordparents_after_insert_update_parent_WoStatus_if_following
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
