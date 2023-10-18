"""
ORM mapping smoke tests

Low value but ensure that the db mapping is correct.
"""

from lute.models.language import Language
from lute.models.term import Term
from lute.models.book import Book, Text, BookTag, Sentence
from lute.db import db
from tests.dbasserts import assert_sql_result, assert_record_count_equals
from datetime import datetime


def test_save_new_language(empty_db):
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


def test_term(empty_db, english):
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


def test_save_book(empty_db, english):
    """
    Check book mappings.
    """

    b = Book()
    b.title = 'hi'
    b.language = english

    t = Text(b, 'some text', 1)

    s = Sentence()
    s.text_content = 'some text'
    s.order = 1

    t.add_sentence(s)

    b.texts.append(t)

    bt = BookTag.make_book_tag('hola')
    b.book_tags.append(bt)

    db.session.add(b)
    db.session.commit()

    # TODO book: update word count
    sql = "select BkID, BkTitle, BkLgID, BkWordCount from books"
    assert_sql_result(sql, ['1; hi; 1; None'], 'book')

    sql = "select TxID, TxBkID, TxText from texts"
    assert_sql_result(sql, ['1; 1; some text'], 'texts')

    sql = "select * from sentences"
    assert_sql_result(sql, ['1; 1; 1; some text'], 'sentences')

    sql = "select * from booktags"
    assert_sql_result(sql, ['1; 1'], 'booktags')

    sql = "select * from tags2"
    assert_sql_result(sql, ['1; hola; '], 'tags2')


def test_save_text_sentences_replaced_in_db(empty_db, english):
    """
    Sentences should only be generated when a Text is saved with the ReadDate saved.
    Sentences are only used for reference lookups.
    """
    b = Book('hola', english)
    t = Text(b, "Tienes un perro. Un gato.")

    db.session.add(t)
    db.session.commit()
    assert_record_count_equals('sentences', 0, 'no sentences')

    t.read_date = datetime.now()
    db.session.add(t)
    db.session.commit()
    assert_record_count_equals('sentences', 2, '2 sentences')

    t.text = "Tengo un coche."
    db.session.add(t)
    db.session.commit()
    assert_record_count_equals('sentences', 1, 'back to 1 sentences')


# TODO db relationships: delete lang should delete everything related
# TODO db relationships: delete book should delete everything related
