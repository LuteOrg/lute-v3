"""
Read service tests.
"""

# from lute.db import db
from lute.language import service
from tests.dbasserts import assert_sql_result


def test_get_all_lang_defs(app_context):
    "Can get all predefined languages."
    defs = service.get_defs()
    engs = [d for d in defs if d["language"].name == "English"]
    assert len(engs) == 1, "have english"
    eng = engs[0]
    assert len(eng["books"]) == 2, "tutorial and follow-up"
    titles = [b.title for b in eng["books"]]
    assert titles == ["Tutorial", "Tutorial follow-up"], "book titles"


def test_load_def_loads_lang_and_stories(empty_db):
    "Can load a language."
    story_sql = "select bktitle from books"
    lang_sql = "select LgName from languages"
    assert_sql_result(lang_sql, [], "no langs")
    assert_sql_result(story_sql, [], "nothing loaded")

    service.load_language_def("English")
    assert_sql_result(lang_sql, ["English"], "eng loaded")
    assert_sql_result(story_sql, ["Tutorial", "Tutorial follow-up"], "stories loaded")
