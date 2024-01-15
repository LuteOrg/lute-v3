DROP TRIGGER IF EXISTS trig_words_after_update_WoStatus_if_following_parent;

CREATE TRIGGER trig_words_after_update_WoStatus_if_following_parent
AFTER UPDATE OF WoStatus, WoFollowParent ON words
FOR EACH ROW
WHEN (old.WoStatus <> new.WoStatus or (old.WoFollowParent = 0 and new.WoFollowParent = 1))
BEGIN
    UPDATE words
    SET WoStatus = new.WoStatus
    WHERE WoID in (
      -- single parent children that are following this term.
      select WpWoID
      from wordparents
      inner join words on WoID = WpWoID
      where WoFollowParent = 1
      and WpParentWoID = old.WoID
      group by WpWoID
      having count(*) = 1

      UNION

      -- The parent of this term,
      -- if this term has a single parent and has "follow parent"
      select WpParentWoID
      from wordparents
      inner join words on WoID = WpWoID
      where WoFollowParent = 1
      and WoID = old.WoID
      group by WpWoID
      having count(*) = 1
    );
END;


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
      WHERE WoFollowParent = 1
      AND WoID = new.WpWoID
    );
END;


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
