"""
Read service tests.
"""

from lute.models.term import Term
from lute.book.model import Book, Repository
from lute.read.service import set_unknowns_to_known, start_reading
from lute.db import db

from tests.dbasserts import assert_record_count_equals, assert_sql_result


def test_set_unknowns_to_known(english, app_context):
    "Unknowns (status 0) or new are set to well known."
    t = Term(english, "dog")
    db.session.add(t)
    db.session.commit()

    b = Book()
    b.title = "blah"
    b.language_id = english.id
    b.text = "Dog CAT dog cat."
    r = Repository(db)
    dbbook = r.add(b)
    r.commit()

    sql = "select WoTextLC, WoStatus from words order by WoText"
    assert_sql_result(sql, ["dog; 1"], "before start")

    start_reading(dbbook, 1, db.session)
    assert_sql_result(sql, ["cat; 0", "dog; 1"], "after start")

    tx = dbbook.texts[0]
    tx.text = "Dog CAT dog cat extra."
    db.session.add(tx)
    db.session.commit()

    set_unknowns_to_known(tx)
    assert_sql_result(sql, ["cat; 99", "dog; 1", "extra; 99"], "after set")


def test_smoke_start_reading(english, app_context):
    "Smoke test book."
    b = Book()
    b.title = "blah"
    b.language_id = english.id
    b.text = "Here is some content.  Here is more."
    r = Repository(db)
    dbbook = r.add(b)
    r.commit()

    assert_record_count_equals("select * from sentences", 0, "before start")
    start_reading(dbbook, 1, db.session)
    assert_record_count_equals("select * from sentences", 2, "after start")


def test_start_reading_creates_Terms_for_unknown_words(english, app_context):
    "Unknown (status 0) terms are created for all new words."
    t = Term(english, "dog")
    db.session.add(t)
    db.session.commit()

    b = Book()
    b.title = "blah"
    b.language_id = english.id
    b.text = "Dog CAT dog cat."
    r = Repository(db)
    dbbook = r.add(b)
    r.commit()

    sql = "select WoTextLC from words order by WoText"
    assert_sql_result(sql, ["dog"], "before start")

    paragraphs = start_reading(dbbook, 1, db.session)
    textitems = [
        ti
        for para in paragraphs
        for sentence in para
        for ti in sentence.textitems
        if ti.is_word and ti.wo_id is None
    ]
    assert (
        len(textitems) == 0
    ), f"All text items should have a term, but got {textitems}"
    assert_sql_result(sql, ["cat", "dog"], "after start")
