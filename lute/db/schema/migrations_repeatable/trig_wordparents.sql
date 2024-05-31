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


-- Delete old bad trigger.
DROP TRIGGER IF EXISTS trig_wordparents_after_delete_change_WoSyncStatus;

/*
-- This trigger isn't correct, per issue 416: When changing a term's
-- parents, the existing parent might be deleted first before adding
-- the new parent.  If this trigger gets fired before the new parent
-- is assigned, the term will be set to WoSyncStatus = 0, even if the
-- user wants the term to follow the new parent's status.  Since we
-- can't say for sure when sqlalchemy will actually make database
-- changes for child records (i.e., will adding new children happen
-- before deleting old?), this trigger on its own isn't good enough.


CREATE TRIGGER trig_wordparents_after_delete_change_WoSyncStatus
-- created by db/schema/migrations_repeatable/trig_wordparents.sql
--
-- This is a data sanity method only: if all of a term's parents are deleted,
-- then the term must have WoSyncStatus = 0.
--
-- Issue 416: We can't simply set WoSyncStatus = 0 on parent deletion,
-- because the user may have _changed_ the parents, but still want to
-- follow the status for the new parent.
BEFORE DELETE ON wordparents
FOR EACH ROW
BEGIN
    UPDATE words
    SET WoSyncStatus = 0
    WHERE WoID = old.WpWoID
    AND NOT EXISTS (
        SELECT 1 FROM wordparents
        WHERE WpWoID = OLD.WpWoID
        AND WpParentWoID != OLD.WpParentWoID
    );
END;
*/
