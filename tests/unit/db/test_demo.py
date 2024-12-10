"""
Tests for managing the demo data.

Prior to https://github.com/LuteOrg/lute-v3/issues/534, the baseline
db had languages and stories pre-loaded.  This created a lot of db
file thrash whenever that data changed.

In the new setup, the baseline db only contains a flag, "LoadDemoData"
(true/false), which is initially set to True.  When the app first
starts up, if that flag is True, it loads the demo data, and sets
"LoadDemoData" to False, and "IsDemoData" to True.

If the LoadDemoData flag is set, the demo data is loaded from the
startup scripts (devstart and lute.main)

"""

from sqlalchemy import text
import pytest
from lute.db import db
from lute.db.demo import (
    set_load_demo_flag,
    remove_load_demo_flag,
    should_load_demo_data,
    contains_demo_data,
    remove_flag,
    delete_demo_data,
    tutorial_book_id,
    load_demo_data,
)
import lute.parse.registry
from tests.dbasserts import assert_record_count_equals, assert_sql_result


# ========================================
# See notes at top of file re these tests.
# ========================================


def test_new_db_doesnt_contain_anything(app_context):
    "New db created from the baseline has the demo flag set."
    assert should_load_demo_data(db.session) is True, "has LoadDemoData flag."
    assert contains_demo_data(db.session) is False, "no demo data."


def test_empty_db_not_loaded_if_load_flag_not_set(app_context):
    "Even if it's empty, nothing happens."
    remove_load_demo_flag(db.session)
    assert contains_demo_data(db.session) is False, "no demo data."
    assert_record_count_equals("select * from languages", 0, "empty")
    load_demo_data(db.session)
    assert contains_demo_data(db.session) is False, "no demo data."
    assert should_load_demo_data(db.session) is False, "still no reload."
    assert_record_count_equals("select * from languages", 0, "still empty")


def test_smoke_test_load_demo_works(app_context):
    "Wipe everything, but set the flag and then start."
    assert should_load_demo_data(db.session) is True, "should reload demo data."
    load_demo_data(db.session)
    assert contains_demo_data(db.session) is True, "demo loaded."
    assert tutorial_book_id(db.session) > 0, "Have tutorial"
    assert should_load_demo_data(db.session) is False, "loaded once, don't reload."


def test_load_not_run_if_data_exists_even_if_flag_is_set(app_context):
    assert should_load_demo_data(db.session) is True, "should reload demo data."
    load_demo_data(db.session)
    assert tutorial_book_id(db.session) > 0, "Have tutorial"
    assert should_load_demo_data(db.session) is False, "loaded once, don't reload."

    remove_flag(db.session)
    set_load_demo_flag(db.session)
    assert should_load_demo_data(db.session) is True, "should re-reload demo data."
    load_demo_data(db.session)  # if this works, it didn't throw :-P
    assert should_load_demo_data(db.session) is False, "already loaded once."


def test_removing_flag_means_not_demo(app_context):
    "Unsetting the flag means the db is not a demo."
    assert should_load_demo_data(db.session) is True, "should reload demo data."
    load_demo_data(db.session)
    assert contains_demo_data(db.session) is True, "demo loaded."
    remove_flag(db.session)
    assert contains_demo_data(db.session) is False, "not a demo now."


def test_wiping_db_clears_flag(app_context):
    "No longer a demo if the demo is wiped out!"
    assert should_load_demo_data(db.session) is True, "should reload demo data."
    load_demo_data(db.session)
    assert contains_demo_data(db.session) is True, "demo loaded."
    delete_demo_data(db.session)
    assert contains_demo_data(db.session) is False, "not a demo."


def test_wipe_db_only_works_if_flag_is_set(app_context):
    "Can only wipe a demo db!"
    assert should_load_demo_data(db.session) is True, "should reload demo data."
    load_demo_data(db.session)
    assert contains_demo_data(db.session) is True, "demo loaded."
    remove_flag(db.session)
    with pytest.raises(Exception):
        delete_demo_data(db.session)


def test_tutorial_id_returned_if_present(app_context):
    "Sanity check."
    assert should_load_demo_data(db.session) is True, "should reload demo data."
    load_demo_data(db.session)
    assert tutorial_book_id(db.session) > 0, "have tutorial"

    sql = 'update books set bktitle = "xxTutorial" where bktitle = "Tutorial"'
    db.session.execute(text(sql))
    db.session.commit()
    assert tutorial_book_id(db.session) is None, "no tutorial"

    sql = 'update books set bktitle = "Tutorial" where bktitle = "xxTutorial"'
    db.session.execute(text(sql))
    db.session.commit()
    assert tutorial_book_id(db.session) > 0, "have tutorial again"

    delete_demo_data(db.session)
    assert tutorial_book_id(db.session) is None, "no tutorial"


# Loading.


@pytest.mark.dbreset
def test_rebaseline(app_context):
    """
    This test is also used from "inv db.reset" in tasks.py
    (see .pytest.ini).
    """
    assert contains_demo_data(db.session) is False, "not a demo."
    assert_record_count_equals("languages", 0, "wiped out")

    # Wipe out all user settings!!!  When user installs and first
    # starts up, the user settings need to be loaded with values from
    # _their_ config and environment.
    sql = "delete from settings where StKeyType = 'user'"
    db.session.execute(text(sql))
    db.session.commit()

    set_load_demo_flag(db.session)

    sql = "select stkeytype, stkey, stvalue from settings"
    assert_sql_result(sql, ["system; LoadDemoData; 1"], "only this key is set.")


@pytest.fixture(name="_restore_japanese_parser")
def fixture_restore_mecab_support():
    """
    "Teardown" method to restore jp parser if it was removed.
    """
    k = "japanese"
    assert k in lute.parse.registry.__LUTE_PARSERS__, "have jp parser, sanity check"
    old_val = lute.parse.registry.__LUTE_PARSERS__[k]

    yield

    if k not in lute.parse.registry.__LUTE_PARSERS__:
        lute.parse.registry.__LUTE_PARSERS__[k] = old_val
