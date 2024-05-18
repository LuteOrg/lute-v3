"""
Tests for managing the demo data.
"""

from sqlalchemy import text
import pytest
from lute.db import db
from lute.db.demo import (
    contains_demo_data,
    remove_flag,
    delete_demo_data,
    tutorial_book_id,
    load_demo_data,
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
    assert k in lute.parse.registry.__LUTE_PARSERS__, "have jp parser, sanity check"
    old_val = lute.parse.registry.__LUTE_PARSERS__[k]

    yield

    if k not in lute.parse.registry.__LUTE_PARSERS__:
        lute.parse.registry.__LUTE_PARSERS__[k] = old_val
