"""
Language model tests - getting, saving, etc.

Low value but ensure that the db mapping is correct.
"""

from lute.models.language import Language
from lute.db import db
from tests.dbasserts import assert_sql_result


def test_demo_has_preloaded_languages(_demo_db):
    """
    When users get the initial demo, it has English, French, etc,
    pre-defined.
    """
    sql = """
    select LgName
    from languages
    where LgName in ('English', 'French')
    order by LgName
    """
    assert_sql_result(sql, [ 'English', 'French' ], 'sanity check loaded')


def test_save_new_language_smoke_test(_empty_db):
    """
    Validating model save only.
    """
    sql = "select LgName from languages";
    assert_sql_result(sql, [], 'empty table')

    lang = Language()
    lang.LgName = 'abc'
    lang.LgDict1URI = 'something'

    db.session.add(lang)
    db.session.commit()

    assert_sql_result(sql, ['abc'], 'have language')
