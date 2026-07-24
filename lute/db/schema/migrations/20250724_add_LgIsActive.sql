-- Add LgIsActive column to languages table.
-- Defaults to 1 (active) for all existing languages.
ALTER TABLE languages ADD COLUMN LgIsActive INTEGER NOT NULL DEFAULT 1;
