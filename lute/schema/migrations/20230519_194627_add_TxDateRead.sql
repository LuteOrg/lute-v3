-- Add field
alter table texts add column TxReadDate datetime null;

-- Mark existing active books read up to current page.
update texts set TxReadDate = datetime('now')
where TxID in (
  select TxID
  from books
  inner join texts on (
    -- correlated subquery: get all TxIDs in the book
    -- where the ID is <= the current book TxID
    TxBkID = BkID and
    TxID <= (select binner.BkCurrentTxID from books binner where binner.BkID = books.BkID)
  )
  where BkArchived = 0
);

-- Mark all archived books as completely read
update texts set TxReadDate = datetime('now')
where TxID in (
  select TxID
  from books
  inner join texts on TxBkID = BkID
  where BkArchived = 1
);
