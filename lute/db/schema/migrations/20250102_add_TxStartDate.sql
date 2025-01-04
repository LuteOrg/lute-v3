-- Add field
alter table texts add column TxStartDate datetime null;

-- Originally I had set the TxStartDate using best guesses, but now
-- feel that that isn't justified.  Too many assumptions, too much to
-- mess up.

/*
-- Assume that pages were started 10 mins before the TxReadDate.
update texts set TxStartDate = datetime(TxReadDate, '-10 minutes') WHERE TxReadDate is not null;

-- Set the start date for the current text in each book if needed (i.e. if any page has been marked
-- read in that book already).
-- This assumes e.g. that the user clicked "mark as read" and immediately started the next page.
UPDATE texts
SET TxStartDate = (
    SELECT MAX(T.TxReadDate)
    FROM texts T
    WHERE T.TxReadDate IS NOT NULL
      AND T.TxBkID = texts.TxBkID
)
WHERE TxStartDate IS NULL
AND TxID IN (
    SELECT BkCurrentTxID
    FROM books
    WHERE BkCurrentTxID <> 0
)
AND TxBkID IN (
    SELECT DISTINCT TxBkID
    FROM texts
    WHERE TxReadDate IS NOT NULL
);
*/

-- After check:
/*
select TxID, TxStartDate, TxReadDate from texts
WHERE TxID IN (
    SELECT BkCurrentTxID
    FROM books
    WHERE BkCurrentTxID <> 0
)
AND TxReadDate IS NULL;
*/
