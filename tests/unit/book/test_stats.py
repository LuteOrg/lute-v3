"""
Book stats tests.
"""

import pytest

from lute.db import db
from lute.term.model import Term, Repository
from lute.book.stats import get_status_distribution, refresh_stats, mark_stale

from tests.utils import make_text, make_book
from tests.dbasserts import assert_record_count_equals, assert_sql_result


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



def do_refresh():
    refresh_stats()


@pytest.fixture(name='test_book')
def fixture_make_book(empty_db, spanish):
    b = make_book("Hola.", "Hola tengo un gato.", spanish)
    db.session.add(b)
    db.session.commit()
    return b


def add_terms(lang, terms):
    "Create and add term."
    repo = Repository(db)
    for s in terms:
        term = Term()
        term.language = lang
        term.language_id = lang.id
        term.text = s
        repo.add(term)
    repo.commit()


def assert_stats(expected):
    sql = "select wordcount, distinctterms, distinctunknowns, unknownpercent from bookstats"
    assert_sql_result(
        sql,
        expected
    )


def test_cache_loads_when_prompted(test_book):
    assert_record_count_equals("bookstats", 0, "nothing loaded")
    do_refresh()
    assert_record_count_equals("bookstats", 1, "loaded")


def test_stats_smoke_test(test_book, spanish):
    add_terms(spanish, [
        "gato", "TENGO"
    ])
    do_refresh()
    assert_stats(["4; 4; 2; 50"])


def test_stats_calculates_rendered_text(test_book, spanish):
    # text is "Hola tengo un gato."
    add_terms(spanish, ["tengo un"])
    do_refresh()
    assert_stats(["4; 3; 2; 67"])


def test_stats_only_update_existing_books_if_specified(test_book, spanish):
    add_terms(spanish, ["gato", "TENGO"])
    do_refresh()
    assert_stats(["4; 4; 2; 50"])

    add_terms(spanish, ["hola"])
    do_refresh()
    assert_stats(["4; 4; 2; 50"])

    mark_stale(test_book)
    do_refresh()
    assert_stats(["4; 4; 1; 25"])
