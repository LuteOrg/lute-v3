-- book audio fields.

ALTER TABLE books ADD COLUMN BkAudioFilename TEXT NULL;
ALTER TABLE books ADD COLUMN BkAudioCurrentPos REAL NULL;
ALTER TABLE books ADD COLUMN BkAudioBookmarks TEXT NULL;
