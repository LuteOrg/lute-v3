"""
Data cleanup routines.

Sometimes required as data management changes.
These cleanup routines will be called by the app_factory.
"""

from lute.db import db
from lute.models.book import Text


def _set_texts_word_count():
    """
    texts.TxWordCount should be set for all texts.

    Fixing a design error: the counts should have been stored here,
    instead of only in books.BkWordCount.

    Ref https://github.com/jzohrab/lute-v3/issues/95
    """
    calc_counts = db.session.query(Text).filter(Text.word_count.is_(None)).all()

    # Don't recalc with invalid parsers!!!!
    recalc = [t for t in calc_counts if t.book.language.is_supported]

    if len(recalc) == 0:
        # Nothing to calculate, quit.
        return

    for t in recalc:
        pt = t.book.language.get_parsed_tokens(t.text)
        words = [w for w in pt if w.is_word]
        t.word_count = len(words)
        db.session.add(t)
    db.session.commit()


def clean_data():
    "Clean all data as required."
    _set_texts_word_count()
