"""
Show bookmarks in datatables.
"""

from lute.utils.data_tables import DataTablesSqliteQuery


def get_data_tables_list(parameters, book_id, session):
    "Bookmark json data for datatables."

    base_sql = f"""
      SELECT tb.TbID, tb.TbTxID, tb.TbTitle, tx.TxOrder
      FROM textbookmarks as tb
      INNER JOIN texts as tx ON tb.TbTxID = tx.TxID
      WHERE tx.TxBkID = { book_id }
    """

    connection = session.connection()
    return DataTablesSqliteQuery.get_data(base_sql, parameters, connection)
