"""
TermTage mapping tests.
"""

from lute.models.term import Term, TermTag
from lute.db import db
from lute.termtag.routes import delete as route_delete
from tests.dbasserts import assert_record_count_equals


def test_deleting_termtag_removes_wordtags_table_record(empty_db, spanish):
    "Association record should be deleted if tag is deleted."

    tg = TermTag("tag")
    db.session.add(tg)
    db.session.commit()

    term = Term(spanish, "HOLA")
    term.add_term_tag(tg)
    db.session.add(term)
    db.session.commit()

    sqlterms = "select * from words"
    assert_record_count_equals(sqlterms, 1, "term sanity check on save")

    sqltags = "select * from tags"
    assert_record_count_equals(sqltags, 1, "tag sanity check on save")

    sqlassoc = "select * from wordtags"
    assert_record_count_equals(sqlassoc, 1, "word tag associations exist")

    route_delete(tg.id)

    assert_record_count_equals(sqlterms, 1, "term stays")
    assert_record_count_equals(sqltags, 0, "tag removed")
    assert_record_count_equals(sqlassoc, 0, "associations removed")
