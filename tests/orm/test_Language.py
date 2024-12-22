"""
Language mapping tests.
"""

import json
from lute.models.language import Language, LanguageDictionary
from lute.models.repositories import LanguageRepository
from lute.read.service import Service as ReadService
from lute.db import db
from tests.dbasserts import assert_sql_result, assert_record_count_equals
from tests.utils import make_text, add_terms


def test_save_new_language(empty_db):
    """
    Check language mappings and defaults.
    """
    sql = """select LgName, LgRightToLeft,
    LgShowRomanization, LgRegexpSplitSentences
    from languages"""
    assert_sql_result(sql, [], "empty table")

    lang = Language()
    lang.name = "abc"

    db.session.add(lang)
    db.session.commit()
    assert_sql_result(sql, ["abc; 0; 0; .!?"], "have language, defaults as expected")

    lang.right_to_left = True
    db.session.add(lang)
    db.session.commit()
    assert_sql_result(sql, ["abc; 1; 0; .!?"], "rtl is True")

    retrieved = db.session.query(Language).filter(Language.name == "abc").first()
    # print(retrieved)
    assert retrieved.name == "abc"
    assert retrieved.right_to_left is True, "retrieved is RTL"
    assert retrieved.show_romanization is False, "retrieved no roman"


def test_language_dictionaries_smoke_test(empty_db):
    "Smoke test for new dictionary structure."
    lang = Language()
    lang.name = "abc"

    ld = LanguageDictionary()
    ld.usefor = "terms"
    ld.dicttype = "embeddedhtml"
    ld.dicturi = "1?[LUTE]"
    ld.sort_order = 1
    lang.dictionaries.append(ld)
    ld2 = LanguageDictionary()
    ld2.usefor = "terms"
    ld2.dicttype = "popuphtml"
    ld2.dicturi = "2?[LUTE]"
    ld2.sort_order = 2
    lang.dictionaries.append(ld2)

    ld3 = LanguageDictionary()
    ld3.usefor = "sentences"
    ld3.dicttype = "popuphtml"
    ld3.dicturi = "3?[LUTE]"
    ld3.sort_order = 3
    lang.dictionaries.append(ld3)

    db.session.add(lang)
    db.session.commit()

    sqldicts = """select LgName, LdUseFor, LdType, LdDictURI
    from languages
    inner join languagedicts on LdLgID = LgID
    order by LdSortOrder"""
    assert_sql_result(
        sqldicts,
        [
            "abc; terms; embeddedhtml; 1?[LUTE]",
            "abc; terms; popuphtml; 2?[LUTE]",
            "abc; sentences; popuphtml; 3?[LUTE]",
        ],
        "dict saved",
    )

    retrieved = db.session.query(Language).filter(Language.name == "abc").first()
    assert len(retrieved.dictionaries) == 3, "have dicts"
    ld = retrieved.dictionaries[0]
    assert ld.dicttype == "embeddedhtml", "type"
    assert ld.dicturi == "1?[LUTE]", "uri"

    exp = """{"1": {"term": ["1?[LUTE]", "*2?[LUTE]"], "sentence": ["*3?[LUTE]"]}}"""
    repo = LanguageRepository(db.session)
    dicts = repo.all_dictionaries()
    assert json.dumps(dicts) == exp


def test_delete_language_removes_book_and_terms(app_context, spanish):
    """
    Test HACKY LanguageRepository.delete() method to ensure deletes cascade.
    """
    add_terms(spanish, ["gato", "perro"])
    t = make_text("hola", "Hola amigo", spanish)
    db.session.add(t)

    ld = LanguageDictionary()
    ld.usefor = "terms"
    ld.dicttype = "embeddedhtml"
    ld.dicturi = "something?[LUTE]"
    ld.sort_order = 1
    spanish.dictionaries.append(ld)
    db.session.add(spanish)

    db.session.commit()

    svc = ReadService(db.session)
    svc.mark_page_read(t.book.id, 1, False)

    sqlterms = "select WoText from words order by WoText"
    sqlbook = "select BkTitle from books where BkTitle = 'hola'"
    sqldict = "select LdDictURI from languagedicts where LdDictURI = 'something?[LUTE]'"
    assert_sql_result(sqlterms, ["gato", "perro"], "initial terms")
    assert_sql_result(sqlbook, ["hola"], "initial book")
    assert_sql_result(sqldict, ["something?[LUTE]"], "dict")
    assert_record_count_equals("select * from wordsread", 1, "saved")

    db.session.delete(spanish)
    db.session.commit()

    assert_sql_result(sqlbook, [], "book deleted")
    assert_sql_result(sqlterms, [], "terms deleted")
    assert_sql_result(sqldict, [], "dicts deleted")
    assert_record_count_equals("select * from wordsread", 0, "deleted")
