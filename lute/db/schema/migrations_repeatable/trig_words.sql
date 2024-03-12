DROP TRIGGER IF EXISTS trig_words_after_update_WoStatus_if_following_parent;

CREATE TRIGGER trig_words_after_update_WoStatus_if_following_parent
-- created by db/schema/migrations_repeatable/trig_words.sql
AFTER UPDATE OF WoStatus, WoSyncStatus ON words
FOR EACH ROW
WHEN (old.WoStatus <> new.WoStatus or (old.WoSyncStatus = 0 and new.WoSyncStatus = 1))
BEGIN
    UPDATE words
    SET WoStatus = new.WoStatus
    WHERE WoID in (
      -- single parent children that are following this term.
      select WpWoID
      from wordparents
      inner join words on WoID = WpWoID
      where WoSyncStatus = 1
      and WpParentWoID = old.WoID
      group by WpWoID
      having count(*) = 1

      UNION

      -- The parent of this term,
      -- if this term has a single parent and has "follow parent"
      select WpParentWoID
      from wordparents
      inner join words on WoID = WpWoID
      where WoSyncStatus = 1
      and WoID = old.WoID
      group by WpWoID
      having count(*) = 1
    );
END;


DROP TRIGGER IF EXISTS trig_words_update_WoStatusChanged;

CREATE TRIGGER trig_words_update_WoStatusChanged
-- created by db/schema/migrations_repeatable/trig_words.sql
AFTER UPDATE OF WoStatus ON words
FOR EACH ROW
WHEN old.WoStatus <> new.WoStatus
BEGIN
    UPDATE words
    SET WoStatusChanged = CURRENT_TIMESTAMP
    WHERE WoID = NEW.WoID;
END;


DROP TRIGGER IF EXISTS trig_words_update_WoCreated_if_no_longer_unknown;

CREATE TRIGGER trig_words_update_WoCreated_if_no_longer_unknown
-- created by db/schema/migrations_repeatable/trig_words.sql
AFTER UPDATE OF WoStatus ON words
FOR EACH ROW
WHEN old.WoStatus <> new.WoStatus and old.WoStatus = 0
BEGIN
    UPDATE words
    SET WoCreated = CURRENT_TIMESTAMP
    WHERE WoID = NEW.WoID;
END;
