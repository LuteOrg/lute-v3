"""
Show terms in datatables.
"""

from lute.db import db
from lute.utils.data_tables import DataTablesSqliteQuery, supported_parser_type_criteria


def get_data_tables_list(parameters):
    "Term json data for datatables."

    base_sql = """SELECT
    0 as chk, w.WoID as WoID, LgName, L.LgID as LgID, w.WoText as WoText, parents.parentlist as ParentText, w.WoTranslation,
    replace(wi.WiSource, '.jpeg', '') as WiSource,
    ifnull(tags.taglist, '') as TagList,
    StText,
    StID
    FROM
    words w
    INNER JOIN languages L on L.LgID = w.WoLgID
    INNER JOIN statuses S on S.StID = w.WoStatus
    LEFT OUTER JOIN (
      SELECT WpWoID as WoID, GROUP_CONCAT(PText, ', ') AS parentlist
      FROM
      (
        select WpWoID, WoText as PText
        from wordparents wp
        INNER JOIN words on WoID = WpParentWoID
        order by WoText
      ) parentssrc
      GROUP BY WpWoID
    ) AS parents on parents.WoID = w.WoID
    LEFT OUTER JOIN (
      SELECT WtWoID as WoID, GROUP_CONCAT(TgText, ', ') AS taglist
      FROM
      (
        select WtWoID, TgText
        from wordtags wt
        INNER JOIN tags t on t.TgID = wt.WtTgID
        order by TgText
      ) tagssrc
      GROUP BY WtWoID
    ) AS tags on tags.WoID = w.WoID
    LEFT OUTER JOIN wordimages wi on wi.WiWoID = w.WoID
    """

    filt_parents_only = parameters["filtParentsOnly"]
    filt_age_min = parameters["filtAgeMin"].strip()
    filt_age_max = parameters["filtAgeMax"].strip()
    filt_status_min = int(parameters["filtStatusMin"])
    filt_status_max = int(parameters["filtStatusMax"])
    filt_include_ignored = parameters["filtIncludeIgnored"]

    typecrit = supported_parser_type_criteria()
    wheres = [f"L.LgParserType in ({typecrit})"]
    if filt_parents_only == "true":
        wheres.append("parents.parentlist IS NULL")
    if filt_age_min:
        filt_age_min = int(filt_age_min)
        wheres.append(
            f"cast(julianday('now') - julianday(w.wocreated) as int) >= {filt_age_min}"
        )
    if filt_age_max:
        filt_age_max = int(filt_age_max)
        wheres.append(
            f"cast(julianday('now') - julianday(w.wocreated) as int) <= {filt_age_max}"
        )

    status_wheres = ["StID <> 98"]
    if filt_status_min > 0:
        status_wheres.append(f"StID >= {filt_status_min}")
    if filt_status_max > 0:
        status_wheres.append(f"StID <= {filt_status_max}")

    status_wheres = " AND ".join(status_wheres)
    if filt_include_ignored == "true":
        status_wheres = f"({status_wheres} OR StID = 98)"
    wheres.append(status_wheres)

    where = " AND ".join(wheres)
    full_base_sql = base_sql + " WHERE " + where

    session = db.session
    connection = session.connection()

    return DataTablesSqliteQuery.get_data(full_base_sql, parameters, connection)
