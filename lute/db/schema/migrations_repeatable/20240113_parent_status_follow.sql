DROP TRIGGER IF EXISTS trig_words_update_WoStatusChanged_parent_follow;

CREATE TRIGGER trig_words_update_WoStatusChanged_parent_follow
AFTER UPDATE OF WoStatus ON words
FOR EACH ROW
WHEN old.WoStatus <> new.WoStatus
BEGIN
    UPDATE words
    SET WoStatus = new.WoStatus
    WHERE WoID in (
      select WpWoID from wordparents
      group by WpWoID having count(*) = 1
    )
    AND WoID in (
      select WpWoID from wordparents
      where WpParentWoID = new.WoID
    )
    AND WoFollowParent = 1;
END;
