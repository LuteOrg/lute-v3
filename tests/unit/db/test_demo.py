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
from lute.db.demo import Service
import lute.parse.registry
from tests.dbasserts import assert_record_count_equals, assert_sql_result


# ========================================
# See notes at top of file re these tests.
# ========================================


@pytest.fixture(name="service")
def _service(app_context):
    return Service(db.session)


def test_new_db_doesnt_contain_anything(service):
    "New db created from the baseline has the demo flag set."
    assert service.should_load_demo_data() is True, "has LoadDemoData flag."
    assert service.contains_demo_data() is False, "no demo data."


def test_empty_db_not_loaded_if_load_flag_not_set(service):
    "Even if it's empty, nothing happens."
    service.remove_load_demo_flag()
    assert service.contains_demo_data() is False, "no demo data."
    assert_record_count_equals("select * from languages", 0, "empty")
    service.load_demo_data()
    assert service.contains_demo_data() is False, "no demo data."
    assert service.should_load_demo_data() is False, "still no reload."
    assert_record_count_equals("select * from languages", 0, "still empty")


def test_smoke_test_load_demo_works(service):
    "Wipe everything, but set the flag and then start."
    assert service.should_load_demo_data() is True, "should reload demo data."
    service.load_demo_data()
    assert service.contains_demo_data() is True, "demo loaded."
    assert service.tutorial_book_id() > 0, "Have tutorial"
    assert service.should_load_demo_data() is False, "loaded once, don't reload."


def test_load_not_run_if_data_exists_even_if_flag_is_set(service):
    "Just in case."
    assert service.should_load_demo_data() is True, "should reload demo data."
    service.load_demo_data()
    assert service.tutorial_book_id() > 0, "Have tutorial"
    assert service.should_load_demo_data() is False, "loaded once, don't reload."

    service.remove_flag()
    service.set_load_demo_flag()
    assert service.should_load_demo_data() is True, "should re-reload demo data."
    service.load_demo_data()  # if this works, it didn't throw :-P
    assert service.should_load_demo_data() is False, "already loaded once."


def test_removing_flag_means_not_demo(service):
    "Unsetting the flag means the db is not a demo."
    assert service.should_load_demo_data() is True, "should reload demo data."
    service.load_demo_data()
    assert service.contains_demo_data() is True, "demo loaded."
    service.remove_flag()
    assert service.contains_demo_data() is False, "not a demo now."


def test_wiping_db_clears_flag(service):
    "No longer a demo if the demo is wiped out!"
    assert service.should_load_demo_data() is True, "should reload demo data."
    service.load_demo_data()
    assert service.contains_demo_data() is True, "demo loaded."
    service.delete_demo_data()
    assert service.contains_demo_data() is False, "not a demo."


def test_wipe_db_only_works_if_flag_is_set(service):
    "Can only wipe a demo db!"
    assert service.should_load_demo_data() is True, "should reload demo data."
    service.load_demo_data()
    assert service.contains_demo_data() is True, "demo loaded."
    service.remove_flag()
    with pytest.raises(Exception):
        service.delete_demo_data()


def test_tutorial_id_returned_if_present(service):
    "Sanity check."
    assert service.should_load_demo_data() is True, "should reload demo data."
    service.load_demo_data()
    assert service.tutorial_book_id() > 0, "have tutorial"

    sql = 'update books set bktitle = "xxTutorial" where bktitle = "Tutorial"'
    db.session.execute(text(sql))
    db.session.commit()
    assert service.tutorial_book_id() is None, "no tutorial"

    sql = 'update books set bktitle = "Tutorial" where bktitle = "xxTutorial"'
    db.session.execute(text(sql))
    db.session.commit()
    assert service.tutorial_book_id() > 0, "have tutorial again"

    service.delete_demo_data()
    assert service.tutorial_book_id() is None, "no tutorial"


# Loading.


@pytest.mark.dbreset
def test_rebaseline(service):
    """
    This test is also used from "inv db.reset" in tasks.py
    (see .pytest.ini).
    """
    assert service.contains_demo_data() is False, "not a demo."
    assert_record_count_equals("languages", 0, "wiped out")

    # Wipe out all user settings!!!  When user installs and first
    # starts up, the user settings need to be loaded with values from
    # _their_ config and environment.
    sql = "delete from settings where StKeyType = 'user'"
    db.session.execute(text(sql))
    db.session.commit()

    service.set_load_demo_flag()

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
