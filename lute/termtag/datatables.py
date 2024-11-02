"""
Show terms in datatables.
"""

from lute.utils.data_tables import DataTablesSqliteQuery


def get_data_tables_list(parameters, session):
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
    connection = session.connection()
    return DataTablesSqliteQuery.get_data(base_sql, parameters, connection)
