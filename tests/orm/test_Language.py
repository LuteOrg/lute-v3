"""
Language mapping tests.
"""

from lute.models.language import Language
from lute.db import db
from tests.dbasserts import assert_sql_result


def test_save_new(empty_db):
    """
    Check language mappings and defaults.
    """
    sql = """select LgName, LgRightToLeft,
    LgShowRomanization, LgRegexpSplitSentences
    from languages"""
    assert_sql_result(sql, [], 'empty table')

    lang = Language()
    lang.name = 'abc'
    lang.dict_1_uri = 'something'

    db.session.add(lang)
    db.session.commit()
    assert_sql_result(sql, ['abc; 0; 0; .!?'], 'have language, defaults as expected')

    lang.right_to_left = True

    db.session.add(lang)
    db.session.commit()
    assert_sql_result(sql, ['abc; 1; 0; .!?'], 'rtl is True')

    retrieved = db.session.query(Language).filter(Language.name == "abc").first()
    # print(retrieved)
    assert retrieved.name == 'abc'
    assert retrieved.right_to_left is True, 'retrieved is RTL'
    assert retrieved.show_romanization is False, 'retrieved no roman'


# TODO db relationships: delete lang should delete everything related
