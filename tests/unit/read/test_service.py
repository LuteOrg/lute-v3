"""
Read service tests.
"""

from lute.models.term import Term
from lute.book.model import Book, Repository
from lute.read.service import Service
from lute.db import db

from tests.dbasserts import assert_record_count_equals, assert_sql_result


def test_mark_page_read(english, app_context):
    "Sanity check, field set and stat added."
    b = Book()
    b.title = "blah"
    b.language_id = english.id
    b.text = "Dog CAT dog cat."
    r = Repository(db.session)
    dbbook = r.add(b)
    r.commit()

    sql_text_started = "select * from texts where TxStartDate is not null"
    sql_text_read = "select * from texts where TxReadDate is not null"
    sql_wordsread = "select * from wordsread"
    assert_record_count_equals(sql_text_started, 0, "not started, sanity check")
    assert_record_count_equals(sql_text_read, 0, "not read")
    assert_record_count_equals(sql_wordsread, 0, "not read")

    svc = Service(db.session)
    svc.mark_page_read(dbbook.id, 1, True)
    assert_record_count_equals(sql_text_started, 0, "still not started!")
    assert_record_count_equals(sql_text_read, 1, "read, text")
    assert_record_count_equals(sql_wordsread, 1, "read, wordsread")

    svc.mark_page_read(dbbook.id, 1, True)
    assert_record_count_equals(sql_text_read, 1, "still read")
    assert_record_count_equals(sql_wordsread, 2, "extra record added")


def test_set_unknowns_to_known(english, app_context):
    "Unknowns (status 0) or new are set to well known."
    t = Term(english, "dog")
    db.session.add(t)
    db.session.commit()

    b = Book()
    b.title = "blah"
    b.language_id = english.id
    b.text = "Dog CAT dog cat."
    r = Repository(db.session)
    dbbook = r.add(b)
    r.commit()

    sql = "select WoTextLC, WoStatus from words order by WoText"
    assert_sql_result(sql, ["dog; 1"], "before start")

    service = Service(db.session)
    service.start_reading(dbbook, 1)
    assert_sql_result(sql, ["cat; 0", "dog; 1"], "after start")

    tx = dbbook.texts[0]
    tx.text = "Dog CAT dog cat extra."
    db.session.add(tx)
    db.session.commit()

    service = Service(db.session)
    service.set_unknowns_to_known(tx)
    assert_sql_result(sql, ["cat; 99", "dog; 1", "extra; 99"], "after set")


def test_smoke_start_reading(english, app_context):
    "Smoke test book."
    b = Book()
    b.title = "blah"
    b.language_id = english.id
    b.text = "Here is some content.  Here is more."
    r = Repository(db.session)
    dbbook = r.add(b)
    r.commit()

    sql_sentence = "select * from sentences"
    sql_text_started = "select * from texts where TxStartDate is not null"
    assert_record_count_equals(sql_sentence, 0, "before start")
    assert_record_count_equals(sql_text_started, 0, "before start")
    service = Service(db.session)
    service.start_reading(dbbook, 1)
    assert_record_count_equals(sql_sentence, 2, "after start")
    assert_record_count_equals(sql_text_started, 1, "text after start")


def test_start_reading_creates_Terms_for_unknown_words(english, app_context):
    "Unknown (status 0) terms are created for all new words."
    t = Term(english, "dog")
    db.session.add(t)
    db.session.commit()

    b = Book()
    b.title = "blah"
    b.language_id = english.id
    b.text = "Dog CAT dog cat."
    r = Repository(db.session)
    dbbook = r.add(b)
    r.commit()

    sql = "select WoTextLC from words order by WoText"
    assert_sql_result(sql, ["dog"], "before start")

    service = Service(db.session)
    paragraphs = service.start_reading(dbbook, 1)
    textitems = [
        ti
        for para in paragraphs
        for sentence in para
        for ti in sentence
        if ti.is_word and ti.wo_id is None
    ]
    assert (
        len(textitems) == 0
    ), f"All text items should have a term, but got {textitems}"
    assert_sql_result(sql, ["cat", "dog"], "after start")
