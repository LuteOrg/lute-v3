-- Manual fix for 20241221_add_wordsread_table.sql, which will be run after this script!
--
-- Hacky fix: a user had a problem during startup and running of the above script
-- at query
--   insert into wordsread (WrLgID, WrTxID, WrReadDate, WrWordCount)
--   select bklgid, txid, txreaddate, txwordcount from texts inner join books on bkid=txbkid where txreaddate is not null;
-- b/c somehow a text had txreaddate not null, but txwordcount = null.
--
-- SHOULD NEVER HAVE HAPPENED but what are you going to do.

update texts set txwordcount = 0 where txwordcount is null and txreaddate is not null;
