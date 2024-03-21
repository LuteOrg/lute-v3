"""
Show terms in datatables.
"""

from lute.db import db
from lute.utils.data_tables import DataTablesSqliteQuery, supported_parser_type_criteria


def get_data_tables_list(parameters):
    "Term json data for datatables."

    base_sql = """SELECT
    0 as chk, w.WoID as WoID, LgName, L.LgID as LgID, w.WoText as WoText, parents.parentlist as ParentText, w.WoTranslation,
    w.WoRomanization,
    replace(wi.WiSource, '.jpeg', '') as WiSource,
    ifnull(tags.taglist, '') as TagList,
    StText,
    StID,
    StAbbreviation,
    case w.WoSyncStatus when 1 then 'y' else '' end as SyncStatus,
    datetime(WoCreated, 'localtime') as WoCreated
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

    typecrit = supported_parser_type_criteria()
    wheres = [f"L.LgParserType in ({typecrit})"]

    # Add "where" criteria for all the filters.

    # Have to check for 'null' for language filter.
    # A new user may filter the language when the demo data is loaded,
    # but on "wipe database" the filtLanguage value stored in localdata
    # may be invalid, resulting in the filtLanguage form control actually
    # sending the **string value** "null" here.
    # The other filter values don't change with the data,
    # so we don't need to check for null.
    # Tricky tricky.
    language_id = parameters["filtLanguage"]
    if language_id == "null" or language_id is None:
        language_id = "0"
    language_id = int(language_id)
    if language_id != 0:
        wheres.append(f"L.LgID == {language_id}")

    if parameters["filtParentsOnly"] == "true":
        wheres.append("parents.parentlist IS NULL")

    sql_age_calc = "cast(julianday('now') - julianday(w.wocreated) as int)"
    age_min = parameters["filtAgeMin"].strip()
    if age_min:
        wheres.append(f"{sql_age_calc} >= {int(age_min)}")
    age_max = parameters["filtAgeMax"].strip()
    if age_max:
        wheres.append(f"{sql_age_calc} <= {int(age_max)}")

    status_wheres = ["StID not in (0, 98)"]
    status_min = int(parameters["filtStatusMin"])
    status_max = int(parameters["filtStatusMax"])
    if status_min > 0:
        status_wheres.append(f"StID >= {status_min}")
    if status_max > 0:
        status_wheres.append(f"StID <= {status_max}")
    status_wheres = " AND ".join(status_wheres)
    if parameters["filtIncludeIgnored"] == "true":
        status_wheres = f"({status_wheres} OR StID = 98)"
    wheres.append(status_wheres)

    # Phew.
    return DataTablesSqliteQuery.get_data(
        base_sql + " WHERE " + " AND ".join(wheres), parameters, db.session.connection()
    )
