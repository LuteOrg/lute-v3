"""
Utility methods for tests.
"""

from lute.models.term import Term
from lute.models.book import Book, Text
from lute.db import db

def add_terms(language, term_array):
    """
    Make and save terms.
    """
    for term in term_array:
        t = Term(language, term)
        db.session.add(t)
    db.session.commit()


def make_text(title, content, language):
    b = Book(title, language)
    t = Text(b, content)
    b.texts.append(t)
    return t
