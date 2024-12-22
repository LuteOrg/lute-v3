-- Clean up bad data, where relationships are invalid.
--
-- Per issue 460, the pragma foreign_keys was not ON, so it's possible
-- (though unlikely) that some data in the db is bad/unreachable.
--
-- This is being done as a one-time fix, rather than as a repeatable
-- migration, as it would be very annoying if the data model changed
-- and I forgot to update the script!!

DELETE FROM languagedicts WHERE LdLgID NOT IN (SELECT LgID FROM languages);
DELETE FROM wordsread WHERE WrLgID NOT IN (SELECT LgID FROM languages);

DELETE FROM books WHERE BkLgID NOT IN (SELECT LgID FROM languages);
DELETE FROM bookstats WHERE BkID NOT IN (SELECT BkID FROM books);
DELETE FROM booktags WHERE BtBkID NOT IN (SELECT BkID FROM books) OR BtT2ID NOT IN (SELECT T2ID FROM tags2);

DELETE FROM texts WHERE TxBkID NOT IN (SELECT BkID FROM books);
DELETE FROM textbookmarks WHERE TbTxID NOT IN (SELECT TxID FROM texts);
DELETE FROM sentences WHERE SeTxID NOT IN (SELECT TxID FROM texts);
DELETE FROM wordsread WHERE WrTxID IS NOT NULL AND WrTxID NOT IN (SELECT TxID FROM texts);

DELETE FROM wordtags WHERE WtWoID NOT IN (SELECT WoID FROM words) OR WtTgID NOT IN (SELECT TgID FROM tags);
DELETE FROM wordimages WHERE WiWoID NOT IN (SELECT WoID FROM words);
DELETE FROM wordflashmessages WHERE WfWoID NOT IN (SELECT WoID FROM words);
DELETE FROM wordparents WHERE WpWoID NOT IN (SELECT WoID FROM words) OR WpParentWoID NOT IN (SELECT WoID FROM words);
