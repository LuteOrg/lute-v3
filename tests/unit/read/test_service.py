"""
Read service tests.
"""

from lute.models.term import Term
from lute.read.service import find_all_Terms_in_string
from lute.db import db
from tests.dbasserts import assert_sql_result


def test_find_all_in_string(spanish, _empty_db):
    terms = [ 'perro', 'gato', 'un gato' ]
    for term in terms:
        t = Term(spanish, term)
        db.session.add(t)
    db.session.commit()

    sql = "select count(*) from words"
    assert_sql_result(sql, ['3'], 'sanity check')
    
    found_terms = find_all_Terms_in_string('Hola tengo un gato', spanish)

    assert len(found_terms) == 2, "2 terms found"
    assert found_terms[0].text_lc == 'gato', 'gato found'
    zws = chr(0x200B)
    assert found_terms[1].text_lc == f'un{zws} {zws}gato', 'un gato found'
