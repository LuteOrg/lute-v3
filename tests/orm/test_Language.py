"""
Language mapping tests.
"""

from lute.models.language import Language, LanguageDictionary
from lute.db import db
from tests.dbasserts import assert_sql_result
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
    lang.dict_1_uri = "something"
    lang.sentence_translate_uri = "sentence_uri"

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
    lang.dict_1_uri = "something"
    lang.sentence_translate_uri = "sentence_uri"

    ld = LanguageDictionary()
    ld.usefor = "terms"
    ld.dicttype = "embeddedhtml"
    ld.dicturi = "something?###"
    ld.sort_order = 1
    lang.dictionaries.append(ld)
    ld2 = LanguageDictionary()
    ld2.usefor = "terms"
    ld2.dicttype = "popuphtml"
    ld2.dicturi = "pop?###"
    ld2.sort_order = 2
    lang.dictionaries.append(ld2)

    db.session.add(lang)
    db.session.commit()

    sqldicts = """select LgName, LdType, LdDictURI
    from languages
    inner join languagedicts on LdLgID = LgID
    order by LdSortOrder"""
    assert_sql_result(
        sqldicts,
        [
            "abc; embeddedhtml; something?###",
            "abc; popuphtml; pop?###",
        ],
        "dict saved",
    )

    retrieved = db.session.query(Language).filter(Language.name == "abc").first()
    assert len(retrieved.dictionaries) == 2, "have dicts"
    ld = retrieved.dictionaries[0]
    assert ld.dicttype == "embeddedhtml", "type"
    assert ld.dicturi == "something?###", "uri"


def test_delete_language_removes_book_and_terms(app_context, spanish):
    """
    Test HACKY Language.delete() method to ensure deletes cascade.
    """
    add_terms(spanish, ["gato", "perro"])
    t = make_text("hola", "Hola amigo", spanish)
    db.session.add(t)

    ld = LanguageDictionary()
    ld.usefor = "terms"
    ld.dicttype = "embeddedhtml"
    ld.dicturi = "something?###"
    ld.sort_order = 1
    spanish.dictionaries.append(ld)
    db.session.add(spanish)

    db.session.commit()

    sqlterms = "select WoText from words order by WoText"
    sqlbook = "select BkTitle from books where BkTitle = 'hola'"
    sqldict = "select LdDictURI from languagedicts where LdDictURI = 'something?###'"
    assert_sql_result(sqlterms, ["gato", "perro"], "initial terms")
    assert_sql_result(sqlbook, ["hola"], "initial book")
    assert_sql_result(sqldict, ["something?###"], "dict")

    Language.delete(spanish)

    assert_sql_result(sqlbook, [], "book deleted")
    assert_sql_result(sqlterms, [], "terms deleted")
    assert_sql_result(sqldict, [], "dicts deleted")
