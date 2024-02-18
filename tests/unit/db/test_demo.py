"""
Tests for managing the demo data.
"""

import os
from sqlalchemy import text
import pytest
from lute.db import db
from lute.db.demo import (
    contains_demo_data,
    remove_flag,
    delete_demo_data,
    tutorial_book_id,
    demo_data_path,
    load_demo_data,
    predefined_languages,
    get_demo_language,
)
import lute.parse.registry
from tests.dbasserts import assert_record_count_equals, assert_sql_result


def test_new_db_is_demo(app_context):
    "New db created from the baseline has the demo flag set."
    assert contains_demo_data() is True, "new db contains demo."


def test_removing_flag_means_not_demo(app_context):
    "Unsetting the flag means the db is not a demo."
    remove_flag()
    assert contains_demo_data() is False, "not a demo."


def test_wiping_db_clears_flag(app_context):
    "No longer a demo if the demo is wiped out!"
    delete_demo_data()
    assert contains_demo_data() is False, "not a demo."


def test_wipe_db_only_works_if_flag_is_set(app_context):
    "Can only wipe a demo db!"
    remove_flag()
    with pytest.raises(Exception):
        delete_demo_data()


def test_tutorial_id_returned_if_present(app_context):
    "Sanity check."
    assert tutorial_book_id() > 0, "have tutorial"

    sql = 'update books set bktitle = "xxTutorial" where bktitle = "Tutorial"'
    db.session.execute(text(sql))
    db.session.commit()
    assert tutorial_book_id() is None, "no tutorial"

    sql = 'update books set bktitle = "Tutorial" where bktitle = "xxTutorial"'
    db.session.execute(text(sql))
    db.session.commit()
    assert tutorial_book_id() > 0, "have tutorial again"

    delete_demo_data()
    assert tutorial_book_id() is None, "no tutorial"


# Getting languages from yaml files.


def test_new_english_from_yaml_file():
    """
    Smoke test, can load a new language from yaml definition.
    """
    f = os.path.join(demo_data_path(), "languages", "english.yaml")
    lang = get_demo_language(f)

    assert lang.name == "English"
    assert lang.show_romanization is False, "uses default"
    assert lang.right_to_left is False, "uses default"

    print(lang.dictionaries)
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


def test_get_predefined():
    """
    Returns all the languages using the files in the demo folder.
    """
    langs = predefined_languages()
    langnames = [lang.name for lang in langs]
    for expected in ["English", "French", "Turkish"]:
        assert expected in langnames, expected


# Loading.


@pytest.mark.dbdemoload
def test_load_demo_loads_language_yaml_files(app_context):
    """
    All data is loaded, spot check some.

    This test is also used from "inv db.reset" in tasks.py
    (see .pytest.ini).
    """
    delete_demo_data()
    assert contains_demo_data() is False, "not a demo."
    assert_record_count_equals("languages", 0, "wiped out")

    # Wipe out all settings!!!
    # When user installs, the settings need to be loaded
    # with values from _their_ config and environment.
    sql = "delete from settings"
    db.session.execute(text(sql))
    db.session.commit()

    load_demo_data()
    assert contains_demo_data() is True, "demo loaded"
    checks = [
        "select * from languages where LgName = 'English'",
        "select * from books where BkTitle = 'Tutorial'",
    ]
    for c in checks:
        assert_record_count_equals(c, 1, c + " returned 1")

    sql = "select distinct stkeytype from settings"
    assert_sql_result(sql, ["system"], "only system settings remain")


@pytest.fixture(name="_restore_japanese_parser")
def fixture_restore_mecab_support():
    """
    "Teardown" method to restore jp parser if it was removed.
    """
    k = "japanese"
    assert k in lute.parse.registry.parsers, "have jp parser, sanity check"
    old_val = lute.parse.registry.parsers[k]

    yield

    if k not in lute.parse.registry.parsers:
        lute.parse.registry.parsers[k] = old_val
