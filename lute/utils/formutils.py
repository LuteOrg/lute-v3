"""
Common form methods.
"""

from lute.models.language import Language
from lute.db import db


def language_choices():
    """
    Return the list of languages for select boxes.

    If only one lang exists, only return that,
    otherwise add a '-' dummy entry at the top.
    """
    langs = db.session.query(Language).order_by(Language.name).all()
    supported = [lang for lang in langs if lang.is_supported]
    lang_choices = [(s.id, s.name) for s in supported]
    if len(lang_choices) > 1:
        lang_choices = [(0, "-")] + lang_choices
    return lang_choices
