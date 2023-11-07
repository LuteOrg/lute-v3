"""
Text mapping checks.
"""

from datetime import datetime
from lute.models.book import Book, Text
from lute.db import db
from tests.dbasserts import assert_record_count_equals


def test_save_text_sentences_replaced_in_db(empty_db, english):
    """
    Sentences should only be generated when a Text is saved with the ReadDate saved.
    Sentences are only used for reference lookups.
    """
    b = Book("hola", english)
    t = Text(b, "Tienes un perro. Un gato.")

    db.session.add(t)
    db.session.commit()
    assert_record_count_equals("sentences", 0, "no sentences")

    t.read_date = datetime.now()
    db.session.add(t)
    db.session.commit()
    assert_record_count_equals("sentences", 2, "2 sentences")

    t.text = "Tengo un coche."
    db.session.add(t)
    db.session.commit()
    assert_record_count_equals("sentences", 1, "back to 1 sentences")
