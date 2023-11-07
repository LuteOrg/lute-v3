"""
Show terms in datatables.
"""

from lute.db import db
from lute.utils.data_tables import DataTablesSqliteQuery


def get_data_tables_list(parameters):
    "json data for datatables."
    base_sql = """SELECT
          TgID,
          TgText,
          TgComment,
          ifnull(TermCount, 0) as TermCount
          FROM tags
          left join (
            select WtTgID,
            count(*) as TermCount
            from wordtags
            group by WtTgID
          ) src on src.WtTgID = TgID
    """
    session = db.session
    connection = session.connection()
    return DataTablesSqliteQuery.get_data(base_sql, parameters, connection)
