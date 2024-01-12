"""
TermForm tests.

Tests lute.term.model.Term *domain* objects being saved
and retrieved from DB.
"""

from lute.models.term import Term as DBTerm
from lute.db import db
from lute.term.model import Term, Repository
from lute.term.forms import TermForm


def test_validate(app, app_context, english):
    "A new term is valid."
    repo = Repository(db)
    t = repo.find_or_new(english.id, "CAT")
    with app.test_request_context():
        f = TermForm(obj=t)
    f.language_id.choices = [(english.id, "english")]

    assert f.validate() is True, "no change = valid"


def test_text_change_not_valid(app, app_context, english):
    "Text change raises error."
    dbt = DBTerm(english, "CAT")
    db.session.add(dbt)
    db.session.commit()

    repo = Repository(db)
    t = repo.find_or_new(english.id, "CAT")
    t.text = "dog"
    with app.test_request_context():
        f = TermForm(obj=t)
    f.language_id.choices = [(english.id, "english")]

    is_valid = f.validate()
    assert is_valid is False, "text change = not valid"
    assert f.errors == {"text": ["Can only change term case"]}


def test_duplicate_text_not_valid(app, app_context, english):
    "Duplicate term throws."
    dbt = DBTerm(english, "CAT")
    db.session.add(dbt)
    db.session.commit()

    t = Term()
    t.language_id = english.id
    t.text = "cat"
    with app.test_request_context():
        f = TermForm(obj=t)
    f.language_id.choices = [(english.id, "english")]

    is_valid = f.validate()
    assert is_valid is False, "dup term not valid"
    assert f.errors == {"text": ["Term already exists"]}


def test_update_existing_term_is_valid(app, app_context, english):
    "Can update an existing term."
    dbt = DBTerm(english, "CAT")
    db.session.add(dbt)
    db.session.commit()

    repo = Repository(db)
    t = repo.find_or_new(english.id, "cat")
    t.text = "cat"
    with app.test_request_context():
        f = TermForm(obj=t)
    f.language_id.choices = [(english.id, "english")]

    is_valid = f.validate()
    assert is_valid is True, "updating existing term is ok"
