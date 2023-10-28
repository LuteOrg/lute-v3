"""
TokenCoverage tests.
"""

from lute.db import db
from lute.term.model import Term, Repository
from lute.book.stats import get_status_distribution

from tests.utils import make_text


def add_term(lang, s, status):
    "Create and add term."
    term = Term()
    term.language = lang
    term.language_id = lang.id
    term.text = s
    term.status = status
    repo = Repository(db)
    repo.add(term)
    repo.commit()


def scenario(language, fulltext, terms_and_statuses, expected):
    "Run a scenario."
    t = make_text('Hola', fulltext, language)
    b = t.book
    db.session.add(t)
    db.session.add(b)
    db.session.commit()

    for ts in terms_and_statuses:
        add_term(language, ts[0], ts[1])

    stats = get_status_distribution(b)

    assert stats == expected


def test_two_words(spanish):
    scenario(
        spanish,
        "Tengo un gato.  Tengo un perro.",
        [["gato", 1], ["perro", 2]],
        {
            0: 2,
            1: 1,
            2: 1,
            3: 0,
            4: 0,
            5: 0,
            98: 0,
            99: 0
        })


def test_single_word(spanish):
    scenario(
        spanish,
        "Tengo un gato.  Tengo un perro.",
        [["gato", 3]],
        {
            0: 3,
            1: 0,
            2: 0,
            3: 1,
            4: 0,
            5: 0,
            98: 0,
            99: 0
        })


def test_with_multiword(spanish):
    scenario(
        spanish,
        "Tengo un gato.  Tengo un perro.",
        [["tengo un", 3]],
        {
            0: 2,
            1: 0,
            2: 0,
            3: 1,
            4: 0,
            5: 0,
            98: 0,
            99: 0
        })


def test_chinese_no_term_stats(classical_chinese):
    scenario(
        classical_chinese,
        '這是東西',
        [],
        {
            0: 4,
            1: 0,
            2: 0,
            3: 0,
            4: 0,
            5: 0,
            98: 0,
            99: 0
        })


def test_chinese_with_terms(classical_chinese):
    scenario(
        classical_chinese,
        '這是東西',
        [ ['東西', 1] ],
        {
            0: 2,
            1: 1,
            2: 0,
            3: 0,
            4: 0,
            5: 0,
            98: 0,
            99: 0
        })
