"""
Show books in datatables.
"""

from lute.db import db
from lute.utils.data_tables import DataTablesSqliteQuery, supported_parser_type_criteria


def get_data_tables_list(parameters, is_archived):
    "Book json data for datatables."
    archived = "true" if is_archived else "false"

    base_sql = f"""
    SELECT
        b.BkID As BkID,
        LgName,
        BkTitle,
        case when currtext.TxID is null then 1 else currtext.TxOrder end as PageNum,
        pagecnt.c as PageCount,
        BkArchived,
        tags.taglist AS TagList,
        case when ifnull(b.BkWordCount, 0) = 0 then 'n/a' else b.BkWordCount end as WordCount,
        c.distinctterms as DistinctCount,
        c.distinctunknowns as UnknownCount,
        c.unknownpercent as UnknownPercent,
        case when completed_books.BkID is null then 0 else 1 end as IsCompleted

    FROM books b
    INNER JOIN languages ON LgID = b.BkLgID
    LEFT OUTER JOIN texts currtext ON currtext.TxID = BkCurrentTxID
    INNER JOIN (
        SELECT TxBkID, COUNT(TxID) AS c FROM texts
        GROUP BY TxBkID
    ) pagecnt on pagecnt.TxBkID = b.BkID
    LEFT OUTER JOIN bookstats c on c.BkID = b.BkID

    LEFT OUTER JOIN (
        SELECT BtBkID as BkID, GROUP_CONCAT(T2Text, ', ') AS taglist
        FROM
        (
            SELECT BtBkID, T2Text
            FROM booktags bt
            INNER JOIN tags2 t2 ON t2.T2ID = bt.BtT2ID
            ORDER BY T2Text
        ) tagssrc
        GROUP BY BtBkID
    ) AS tags ON tags.BkID = b.BkID

    LEFT OUTER JOIN (
      SELECT BkID
      FROM books B
      JOIN texts T ON B.BkID = T.TxBkID
      WHERE T.TxID = (
        SELECT MAX(TxID)
        FROM texts
        WHERE TxBkID = B.BkID
      )
      AND T.TxReadDate IS NOT NULL
    ) completed_books on completed_books.BkID = b.BkID

    WHERE b.BkArchived = {archived}
      and languages.LgParserType in ({ supported_parser_type_criteria() })
    """

    # print(base_sql)
    session = db.session
    connection = session.connection()

    return DataTablesSqliteQuery.get_data(base_sql, parameters, connection)
