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


    @staticmethod
    def get_data_tables_list(parameters, is_archived):
        "Book json data for datatables."

        archived = 'true' if is_archived else 'false'

        base_sql = f"""
        SELECT
            b.BkID, LgName,
            BkTitle || CASE
                WHEN currtext.TxID IS NULL THEN ''
                ELSE ' (' || currtext.TxOrder || '/' || pagecnt.c || ')'
            END AS BkTitle,
            pagecnt.c AS PageCount,
            BkArchived,
            tags.taglist AS TagList,
            CASE
                WHEN IFNULL(b.BkWordCount, 0) = 0 THEN 'n/a'
                ELSE b.BkWordCount
            END AS WordCount,
            c.distinctterms AS DistinctCount,
            c.distinctunknowns AS UnknownCount,
            c.unknownpercent AS UnknownPercent
        FROM books b
        INNER JOIN languages ON LgID = b.BkLgID
        LEFT OUTER JOIN texts currtext ON currtext.TxID = BkCurrentTxID
        INNER JOIN (
            SELECT TxBkID, COUNT(TxID) AS c
            FROM texts
            GROUP BY TxBkID
        ) pagecnt ON pagecnt.TxBkID = b.BkID
        LEFT OUTER JOIN bookstats c ON c.BkID = b.BkID
        LEFT OUTER JOIN (
            SELECT BtBkID AS BkID, GROUP_CONCAT(T2Text, ', ') AS taglist
            FROM (
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
