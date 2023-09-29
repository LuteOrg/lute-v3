-- Sqlite doesn't do a lowercase function!  Add it to textlc.

-- Force re-parsing of texts.
delete from texttokens;

alter table texttokens add TokTextLC VARCHAR(100) NOT NULL;
