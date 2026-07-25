"""
Show terms in datatables.
"""

from lute.utils.data_tables import DataTablesSqliteQuery, supported_parser_type_criteria
from lute.models.book import Book
from lute.models.term import Term
from lute.read.render.service import Service as RenderService


def get_data_tables_list(parameters, session):
    "Term json data for datatables."

    base_sql = """SELECT
    w.WoID as WoID, LgName, L.LgID as LgID, w.WoText as WoText, parents.parentlist as ParentText, w.WoTranslation,
    w.WoRomanization,
    WiSource,
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
      /* Special concat used for easy parsing on client. */
      SELECT WpWoID as WoID, GROUP_CONCAT(PText, ';;') AS parentlist
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
      /* Special concat used for easy parsing on client. */
      SELECT WtWoID as WoID, GROUP_CONCAT(TgText, ';;') AS taglist
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

    wheres = _build_where_criteria(parameters, session)

    return DataTablesSqliteQuery.get_data(
        base_sql + " WHERE " + " AND ".join(wheres), parameters, session.connection()
    )


def _build_where_criteria(parameters, session):
    "Build SQL where clause criteria from filters."
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

    # Parents only
    if parameters["filtParentsOnly"] == "true":
        wheres.append("parents.parentlist IS NULL")

    # Age filters
    sql_age_calc = "cast(julianday('now') - julianday(w.wocreated) as int)"
    age_min = parameters["filtAgeMin"].strip()
    if age_min:
        wheres.append(f"{sql_age_calc} >= {int(age_min)}")
    age_max = parameters["filtAgeMax"].strip()
    if age_max:
        wheres.append(f"{sql_age_calc} <= {int(age_max)}")

    # Status filters
    st_range = ["StID != 98"]
    status_min = int(parameters.get("filtStatusMin", "0"))
    status_max = int(parameters.get("filtStatusMax", "99"))
    st_range.append(f"StID >= {status_min}")
    st_range.append(f"StID <= {status_max}")
    st_where = " AND ".join(st_range)
    if parameters["filtIncludeIgnored"] == "true":
        st_where = f"({st_where} OR StID = 98)"
    wheres.append(st_where)

    # Book and page filters
    _add_book_filter(wheres, parameters, session)

    # Term IDs filter
    termids = parameters["filtTermIDs"].strip()
    if termids != "":
        parentsql = f"select WpParentWoID from wordparents where WpWoID in ({termids})"
        wheres.append(f"((w.WoID in ({termids})) OR (w.WoID in ({parentsql})))")

    return wheres


def _add_book_filter(wheres, parameters, session):
    "Add book and page level filters to SQL where clauses."
    if not parameters.get("filtBook") or parameters.get("filtBook") in ("0", "null"):
        return

    book = (
        session.query(Book).filter(Book.id == int(parameters.get("filtBook"))).first()
    )
    if not book:
        return

    if parameters.get("filtBookScope", "all") == "page" and parameters.get(
        "filtPageNum"
    ) not in (None, "0", ""):
        texts = [book.text_at_page(int(parameters.get("filtPageNum")))]
    else:
        texts = book.texts

    words_lc = set()
    service = RenderService(session)
    text_lcs = [
        book.language.parser.get_lowercase(t.token)
        for t in book.language.get_parsed_tokens("\n".join([t.text for t in texts]))
    ]
    words_lc.update(text_lcs)
    words_lc.update(
        service.find_all_multi_word_term_text_lcs_in_content(text_lcs, book.language)
    )

    if not words_lc:
        wheres.append("1 = 0")
        return

    term_ids = [
        r[0]
        for r in session.query(Term.id)
        .filter(
            Term.language_id == book.language_id,
            Term.text_lc.in_(list(words_lc)),
        )
        .all()
    ]

    if not term_ids:
        wheres.append("1 = 0")
        return

    chunks = [term_ids[i : i + 900] for i in range(0, len(term_ids), 900)]
    chunk_wheres = []
    for chunk in chunks:
        chunk_str = ",".join(str(tid) for tid in chunk)
        chunk_wheres.append(
            f"((w.WoID in ({chunk_str})) OR "
            f"(w.WoID in (select WpParentWoID from wordparents where WpWoID in ({chunk_str}))))"
        )
    wheres.append("(" + " OR ".join(chunk_wheres) + ")")
