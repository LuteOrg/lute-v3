"""
ORM mapping smoke tests

Low value but ensure that the db mapping is correct.
"""

from lute.models.language import Language
from lute.db import db
from tests.dbasserts import assert_sql_result


def test_language(_empty_db):
    """
    Check language mappings.
    """
    sql = "select LgName, LgRightToLeft, LgShowRomanization from languages"
    assert_sql_result(sql, [], 'empty table')

    lang = Language()
    lang.name = 'abc'
    lang.dict_1_uri = 'something'

    db.session.add(lang)
    db.session.commit()
    assert_sql_result(sql, ['abc; 0; 0'], 'have language, default rtl = 0, show rom = 0')

    lang.right_to_left = True

    db.session.add(lang)
    db.session.commit()
    assert_sql_result(sql, ['abc; 1; 0'], 'rtl is True')

    retrieved = db.session.query(Language).filter(Language.name == "abc").first()
    # print(retrieved)
    assert retrieved.name == 'abc'
    assert retrieved.right_to_left is True, 'retrieved is RTL'
    assert retrieved.show_romanization is False, 'retrieved no roman'
