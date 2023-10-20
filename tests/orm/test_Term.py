"""
Term mapping tests.
"""

from lute.models.term import Term
from lute.db import db
from tests.dbasserts import assert_sql_result


def test_save(empty_db, english):
    """
    Check term mappings.
    """
    sql = "select WoText, WoTextLC, WoTokenCount from words"
    assert_sql_result(sql, [], 'empty table')

    term = Term()
    term.language = english
    term.text = 'abc'
    term.text_lc = 'abc'
    term.token_count = 1

    db.session.add(term)
    db.session.commit()
    assert_sql_result(sql, ['abc; abc; 1'], 'have term')
