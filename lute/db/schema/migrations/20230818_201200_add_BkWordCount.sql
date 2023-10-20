-- Add field
alter table books add BkWordCount INT;

-- update books set BkWordCount = null;

-- sqlite3 might not support update-from (introduced v3.33 release
-- 14th August 2020), so will use correlated subquery.

-- First load wordcount from existing bookstats table.
update books
set BkWordCount = (
    select wordcount from bookstats
    where bookstats.BkID = books.BkID
);

-- load remaining BkWordCounts from correlated subquery.

-- Load temp table to vastly speed up correlated subquery.
drop table if exists zz_bkwordcount;
create table zz_bkwordcount (zzBkID int, c);

insert into zz_bkwordcount (zzBkID, c)
select
TxBkID, count(*) as c
from texttokens
inner join texts on TxID = TokTxID
where TokIsWord = 1
group by TxBkID;

update books
set BkWordCount = (
    select c from zz_bkwordcount
    where zz_bkwordcount.zzBkID = books.BkID
)
where BkWordCount is null;

drop table zz_bkwordcount;
