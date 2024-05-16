"""
Read service tests.
"""

# from lute.db import db
from lute.language import service
from tests.dbasserts import assert_sql_result


def test_get_all_lang_defs(app_context):
    "Can get all predefined languages."
    defs = service.get_supported_defs()
    engs = [d for d in defs if d["language"].name == "English"]
    assert len(engs) == 1, "have english"
    eng = engs[0]
    assert len(eng["books"]) == 2, "tutorial and follow-up"
    titles = [b.title for b in eng["books"]]
    titles.sort()
    assert titles == ["Tutorial", "Tutorial follow-up"], "book titles"


def test_get_language_def():
    """
    Smoke test, can load a new language from yaml definition.
    """
    lang = service.get_language_def("English")["language"]

    assert lang.name == "English"
    assert lang.show_romanization is False, "uses default"
    assert lang.right_to_left is False, "uses default"

    expected = [
        "terms; embeddedhtml; https://en.thefreedictionary.com/###; True; 1",
        "terms; popuphtml; https://www.collinsdictionary.com/dictionary/english/###; True; 2",
        "sentences; popuphtml; https://www.deepl.com/translator#en/en/###; True; 3",
    ]
    actual = [
        f"{ld.usefor}; {ld.dicttype}; {ld.dicturi}; {ld.is_active}; {ld.sort_order}"
        for ld in lang.dictionaries
    ]
    assert actual == expected, "dictionaries"


def test_load_def_loads_lang_and_stories(empty_db):
    "Can load a language."
    story_sql = "select bktitle from books order by BkTitle"
    lang_sql = "select LgName from languages"
    assert_sql_result(lang_sql, [], "no langs")
    assert_sql_result(story_sql, [], "nothing loaded")

    lang_id = service.load_language_def("English")
    assert lang_id > 0, "ID returned, used for filtering"
    assert_sql_result(lang_sql, ["English"], "eng loaded")
    assert_sql_result(story_sql, ["Tutorial", "Tutorial follow-up"], "stories loaded")


def test_load_all_defs_loads_lang_and_stories(empty_db):
    "Smoke test, load everything."
    story_sql = "select bktitle from books"
    lang_sql = "select LgName from languages"
    assert_sql_result(lang_sql, [], "no langs")
    assert_sql_result(story_sql, [], "nothing loaded")

    defs = service.get_supported_defs()
    langnames = [d["language"].name for d in defs]
    for n in langnames:
        lang_id = service.load_language_def(n)
        assert lang_id > 0, "Loaded"
