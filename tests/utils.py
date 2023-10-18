"""
Utility methods for tests.
"""

from lute.models.term import Term


def add_terms(db, language, term_array):
    """
    Make and save terms.
    """
    for term in term_array:
        t = Term(language, term)
        db.session.add(t)
    db.session.commit()
