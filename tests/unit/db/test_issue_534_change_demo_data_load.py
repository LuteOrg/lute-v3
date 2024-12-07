"""Tests during redesign for issue 534, change demo data load.
https://github.com/LuteOrg/lute-v3/issues/534

Prior to issue 534, the baseline db had languages and stories
pre-loaded.  This created a lot of db file thrash whenever that data
changed.

In the new setup, the baseline db only contains a flag, "LoadDemoData"
(true/false), which is initially set to True.  When the app first
starts up, if that flag is True, it loads the demo data, and sets
"LoadDemoData" to False, and "IsDemoData" to True.

Since these tests use the app context, the app startup is called,
which goes through all of the above automatically.  Some of these
tests therefore need to re-wipe the database to force a reload.  It's
a bit hacky; a better way to do this would be to have db
initialization done completely outside of the application, but that
requires some rework of how the db is initialized and the various data
models loaded.
"""

from sqlalchemy import text
import pytest
from lute.db import db
from lute.db.demo import (
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


def test_new_db_is_demo(app_context):
    "New db created from the baseline has the demo flag set."
    assert contains_demo_data(db.session) is True, "new db contains demo."
    assert should_load_demo_data(db.session) is False, "don't reload demo data."


def todo_tests():
    """Some tests to add

    - wipe db, LoadDemoData should be false
    - wipe db, set LoadDemoData to True, and reload, gets loaded, loaddemodata false at end
    - wipe db, set LoadDemoData to False, and reload, shouldn't reload
    - new db, loaddemodata to true, shouldn't reload, loaddemodata should be false at end

    - sanity checks/overkill
    - no data, is demo = true, loaddemo = true, should reload
    - no data, is demo = true, loaddemo = false, no reload
    - no data, is demo = false, loaddemo = true, should reload
    - no data, is demo = false, loaddemo = false, no reload
    - have data, is demo = true, loaddemo = true, no reload
    - have data, is demo = true, loaddemo = false, no reload
    - have data, is demo = false, loaddemo = true, no reload
    - have data, is demo = false, loaddemo = false, no reload
    """


### def test_removing_flag_means_not_demo(app_context):
###     "Unsetting the flag means the db is not a demo."
###     remove_flag(db.session)
###     assert contains_demo_data(db.session) is False, "not a demo."
###
###
### def test_wiping_db_clears_flag(app_context):
###     "No longer a demo if the demo is wiped out!"
###     delete_demo_data(db.session)
###     assert contains_demo_data(db.session) is False, "not a demo."
###
###
### def test_wipe_db_only_works_if_flag_is_set(app_context):
###     "Can only wipe a demo db!"
###     remove_flag(db.session)
###     with pytest.raises(Exception):
###         delete_demo_data(db.session)
###
###
### def test_tutorial_id_returned_if_present(app_context):
###     "Sanity check."
###     assert tutorial_book_id(db.session) > 0, "have tutorial"
###
###     sql = 'update books set bktitle = "xxTutorial" where bktitle = "Tutorial"'
###     db.session.execute(text(sql))
###     db.session.commit()
###     assert tutorial_book_id(db.session) is None, "no tutorial"
###
###     sql = 'update books set bktitle = "Tutorial" where bktitle = "xxTutorial"'
###     db.session.execute(text(sql))
###     db.session.commit()
###     assert tutorial_book_id(db.session) > 0, "have tutorial again"
###
###     delete_demo_data(db.session)
###     assert tutorial_book_id(db.session) is None, "no tutorial"
###
###
### # Loading.
###
###
### @pytest.mark.dbdemoload
### def test_load_demo_loads_language_yaml_files(app_context):
###     """
###     All data is loaded, spot check some.
###
###     This test is also used from "inv db.reset" in tasks.py
###     (see .pytest.ini).
###     """
###     delete_demo_data(db.session)
###     assert contains_demo_data(db.session) is False, "not a demo."
###     assert_record_count_equals("languages", 0, "wiped out")
###
###     load_demo_data(db.session)
###     assert contains_demo_data(db.session) is True, "demo loaded"
###     checks = [
###         "select * from languages where LgName = 'English'",
###         "select * from books where BkTitle = 'Tutorial'",
###     ]
###     for c in checks:
###         assert_record_count_equals(c, 1, c + " returned 1")
###
###     # Wipe out all user settings!!!  When user installs and first
###     # starts up, the user settings need to be loaded with values from
###     # _their_ config and environment.
###     sql = "delete from settings where StKeyType = 'user'"
###     db.session.execute(text(sql))
###     db.session.commit()
###
###     sql = "select stkeytype, stkey, stvalue from settings"
###     assert_sql_result(sql, ["system; IsDemoData; 1"], "only this key is set.")
###
###
### @pytest.fixture(name="_restore_japanese_parser")
### def fixture_restore_mecab_support():
###     """
###     "Teardown" method to restore jp parser if it was removed.
###     """
###     k = "japanese"
###     assert k in lute.parse.registry.__LUTE_PARSERS__, "have jp parser, sanity check"
###     old_val = lute.parse.registry.__LUTE_PARSERS__[k]
###
###     yield
###
###     if k not in lute.parse.registry.__LUTE_PARSERS__:
###         lute.parse.registry.__LUTE_PARSERS__[k] = old_val
