"""
Language service tests.
"""

from lute.language.service import Service
from lute.db import db
from lute.utils.debug_helpers import DebugTimer
from tests.dbasserts import assert_sql_result


def test_get_all_lang_defs(app_context):
    "Can get all predefined languages."
    service = Service(db.session)
    defs = service.get_supported_defs()
    engs = [d for d in defs if d.language.name == "English"]
    assert len(engs) == 1, "have english"
    eng = engs[0]
    assert len(eng.books) == 2, "tutorial and follow-up"
    titles = [b.title for b in eng.books]
    titles.sort()
    assert titles == ["Tutorial", "Tutorial follow-up"], "book titles"


def test_supported_predefined_languages(app_context):
    "Get supported lang names"
    service = Service(db.session)
    predefs = service.supported_predefined_languages()
    assert len(predefs) > 1, "Have predefined"
    langnames = [lang.name for lang in predefs]
    assert "English" in langnames, "Have English"
    assert "French" in langnames, "Have French"


def test_get_language_def(app_context):
    """
    Smoke test, can load a new language from yaml definition.
    """
    service = Service(db.session)
    lang = service.get_language_def("English").language

    assert lang.name == "English"
    assert lang.show_romanization is False, "uses default"
    assert lang.right_to_left is False, "uses default"

    # pylint: disable=line-too-long
    expected = [
        "terms; embeddedhtml; https://simple.wiktionary.org/wiki/[LUTE]; True; 1",
        "terms; popuphtml; https://www.collinsdictionary.com/dictionary/english/[LUTE]; True; 2",
        "sentences; popuphtml; https://www.deepl.com/translator#en/en/[LUTE]; True; 3",
        "terms; popuphtml; https://conjugator.reverso.net/conjugation-english-verb-[LUTE].html; True; 4",
    ]
    actual = [
        f"{ld.usefor}; {ld.dicttype}; {ld.dicturi}; {ld.is_active}; {ld.sort_order}"
        for ld in lang.dictionaries
    ]
    assert actual == expected, "dictionaries"


def test_load_def_loads_lang_and_stories(app_context):
    "Can load a language."
    story_sql = "select bktitle from books order by BkTitle"
    lang_sql = "select LgName from languages"
    assert_sql_result(lang_sql, [], "no langs")
    assert_sql_result(story_sql, [], "nothing loaded")

    dt = DebugTimer("Loading", False)
    dt.step("start")
    service = Service(db.session)
    dt.step("Service()")
    lang_id = service.load_language_def("English")
    dt.step("load_language_def")
    dt.summary()

    assert lang_id > 0, "ID returned, used for filtering"
    assert_sql_result(lang_sql, ["English"], "eng loaded")
    assert_sql_result(story_sql, ["Tutorial", "Tutorial follow-up"], "stories loaded")


def test_load_all_defs_loads_lang_and_stories(app_context):
    "Smoke test, load everything."
    story_sql = "select bktitle from books"
    lang_sql = "select LgName from languages"
    assert_sql_result(lang_sql, [], "no langs")
    assert_sql_result(story_sql, [], "nothing loaded")

    db.session.flush()
    service = Service(db.session)
    defs = service.get_supported_defs()
    langnames = [d.language.name for d in defs]
    for n in langnames:
        lang_id = service.load_language_def(n)
        assert lang_id > 0, "Loaded"
