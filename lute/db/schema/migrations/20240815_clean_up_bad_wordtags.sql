-- Clean up job per GitHub issue https://github.com/LuteOrg/lute-v3/issues/455
--
-- When users deleted Term Tags through the UI, the records in the wordtags
-- table weren't being deleted properly, which may cause some problems in the future.
-- This script deletes those orphaned wordtags records.

delete from wordtags where WtTgID not in (select TgID from tags);
