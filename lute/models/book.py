"""
Book entity.
"""

from lute.db import db
from lute.utils.data_tables import DataTablesSqliteQuery

class Book(db.Model): # pylint: disable=too-few-public-methods, too-many-instance-attributes
    """
    Book entity.
    """

    __tablename__ = 'books'

    id = db.Column('BkID', db.SmallInteger, primary_key=True)


    def __init__(self):
        pass


    def __repr__(self):
        return f"<Book {self.id} add_title>"


    # TODO book listing: update to new code in lutev2
    @staticmethod
    def get_data_tables_list(parameters, is_archived):
        "Book json data for datatables."

        archived = 'true' if is_archived else 'false'

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
            c.unknownpercent as UnknownPercent

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

        WHERE b.BkArchived = {archived}
        """

        session = db.session
        connection = session.connection()

        return DataTablesSqliteQuery.get_data(base_sql, parameters, connection)
