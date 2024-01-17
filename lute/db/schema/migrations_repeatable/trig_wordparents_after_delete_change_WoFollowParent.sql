DROP TRIGGER IF EXISTS trig_wordparents_after_delete_change_WoFollowParent;

CREATE TRIGGER trig_wordparents_after_delete_change_WoFollowParent
BEFORE DELETE ON wordparents
FOR EACH ROW
BEGIN
    UPDATE words
    SET WoFollowParent = 0
    WHERE WoID IN
    (
      select WpWoID from wordparents
      where WpParentWoID = old.WpParentWoID
    );
END;
