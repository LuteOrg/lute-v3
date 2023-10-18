"""
Read service tests.
"""

from lute.models.term import Term
from lute.read.service import find_all_Terms_in_string
from lute.db import db
from tests.dbasserts import assert_sql_result


def _run_scenario(spanish, content, expected_found):
    found_terms = find_all_Terms_in_string(content, spanish)
    assert len(found_terms) == len(expected_found), 'found count'
    zws = '\u200B'  # zero-width space
    found_terms = [ t.text.replace(zws, '') for t in found_terms ]
    assert found_terms == expected_found


def test_spanish_find_all_in_string(spanish, _empty_db):
    terms = [ 'perro', 'gato', 'un gato' ]
    for term in terms:
        t = Term(spanish, term)
        db.session.add(t)
    db.session.commit()

    _run_scenario(spanish, 'Hola tengo un gato', [ 'gato', 'un gato' ])
    _run_scenario(spanish, 'gato gato gato', [ 'gato' ])
    _run_scenario(spanish, 'No tengo UN PERRO', [ 'perro' ])
    _run_scenario(spanish, 'Hola tengo un    gato', [ 'gato', 'un gato' ])
    _run_scenario(spanish, 'No tengo nada', [])

    terms = [ 'échalo', 'ábrela' ]
    for term in terms:
        t = Term(spanish, term)
        db.session.add(t)
    db.session.commit()

    _run_scenario(spanish, '"Échalo", me dijo.', [ 'échalo' ])
    _run_scenario(spanish, 'gato ábrela Ábrela', [ 'gato', 'ábrela' ])


def test_english_find_all_in_string(english, _empty_db):
    terms = [ "the cat's pyjamas" ]
    for term in terms:
        t = Term(english, term)
        db.session.add(t)
    db.session.commit()

    _run_scenario(english, "This is the cat's pyjamas.", [ "the cat's pyjamas" ])


# TODO turkish: add check
# TODO japanese: add check
# TODO chinese: add check
# TODO arabic: add check
