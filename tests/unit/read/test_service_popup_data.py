"""
Term popup data tests.
"""

from lute.models.term import Term
from lute.read.service import get_popup_data
from lute.db import db


def test_smoke(spanish, app_context):
    "Keep the lights on test, smoke only."
    terms = ["perro", "gato", "un gato"]
    for term in terms:
        t = Term(spanish, term)
        db.session.add(t)
    db.session.commit()

    d = get_popup_data(t.id)
    print(d)


# TODO tests:
# no parent
# single parent same translation - no extra parent data
# single parent with different translation - extra data
# multi parents - extra data
