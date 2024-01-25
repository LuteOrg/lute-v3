"""
Utility methods for tests.
"""

from lute.models.term import Term
from lute.models.book import Book
from lute.read.render.service import get_paragraphs
from lute.db import db


def add_terms(language, term_array):
    """
    Make and save terms.
    """
    for term in term_array:
        t = Term(language, term)
        db.session.add(t)
    db.session.commit()


def make_book(title, content, language):
    """
    Make a book.
    """
    b = Book.create_book(title, language, content)
    return b


def make_text(title, content, language):
    """
    Make a single-page book, return the text.
    """
    b = make_book(title, content, language)
    return b.texts[0]


def get_rendered_string(text, imploder="/", overridestringize=None):
    "Get the stringized rendered content after parsing."

    def stringize(ti):
        zws = "\u200B"
        status = ""
        if ti.wo_status not in [None, 0]:
            status = f"({ti.wo_status})"
        return ti.display_text.replace(zws, "") + status

    usestringize = overridestringize or stringize
    ret = []
    paras = get_paragraphs(text.text, text.book.language)
    for p in paras:
        tis = [t for s in p for t in s.textitems]
        ss = [usestringize(ti) for ti in tis]
        ret.append(imploder.join(ss))
    return "/<PARA>/".join(ret)


def assert_rendered_text_equals(text, expected, msg=""):
    "Check that the rendered string matches the expected."
    actual = get_rendered_string(text)
    # This assertion gives details because the module
    # is registered in tests/__init__.py.
    assert actual == "/<PARA>/".join(expected), msg
