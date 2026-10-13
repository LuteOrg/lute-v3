"""
Book tests.
"""

import pytest
from lute.term.datatables import get_data_tables_list
from lute.db import db
from lute.models.book import Book, Text
from tests.utils import add_terms


@pytest.fixture(name="_dt_params")
def fixture_dt_params():
    "Sample query params."
    columns = [
        {"data": "0", "name": "WoID", "searchable": False, "orderable": False},
        {"data": "1", "name": "WoText", "searchable": True, "orderable": True},
    ]
    params = {
        "draw": "1",
        "columns": columns,
        "order": [{"column": "1", "dir": "asc"}],
        "start": "0",
        "length": "10",
        "search": {"value": "", "regex": False},
        # Filters - set "manually" in the route.
        # Cheating here ... had to look at the request payload
        # in devtools to see what was being sent.
        "filtLanguage": "null",  # Ha!
        "filtParentsOnly": "false",
        "filtAgeMin": "",
        "filtAgeMax": "",
        "filtStatusMin": "0",
        "filtStatusMax": "99",
        "filtIncludeIgnored": "false",
        "filtTermIDs": "",
    }
    return params


def test_smoke_term_datatables_query_runs(app_context, _dt_params):
    """
    Smoke test only, ensure query runs.
    """
    get_data_tables_list(_dt_params, db.session)
    # print(d['data'])
    a = 1
    assert a == 1, "dummy check"


def test_smoke_query_with_filter_params_runs(app_context, _dt_params):
    "Smoke test with filters set."
    _dt_params["filtLanguage"] = "44"
    _dt_params["filtParentsOnly"] = "true"
    _dt_params["filtAgeMin"] = "1"
    _dt_params["filtAgeMax"] = "10"
    _dt_params["filtStatusMin"] = "2"
    _dt_params["filtStatusMax"] = "4"
    _dt_params["filtIncludeIgnored"] = "true"
    _dt_params["filtTermIDs"] = "42,43"
    get_data_tables_list(_dt_params, db.session)


def test_parents_included_in_termids_query(app_context, _dt_params, spanish):
    "For term list viewing from page, it's useful to see parents as well."
    # pylint: disable=unbalanced-tuple-unpacking
    [t, p, g] = add_terms(spanish, ["T", "P", "G"])
    t.add_parent(p)
    p.add_parent(g)
    db.session.add(t)
    db.session.add(p)
    db.session.commit()

    _dt_params["filtTermIDs"] = f"{t.id}"
    d = get_data_tables_list(_dt_params, db.session)
    terms = [t["WoText"] for t in d["data"]]
    terms = sorted(terms)
    assert terms == ["P", "T"]


def test_book_and_page_filtering(app_context, _dt_params, spanish):
    "Filtering terms in datatables by book and page scope."
    # Create a book with two pages
    book = Book("Test Book", spanish)
    Text(book, "Hola tengo un gato.", 1)
    Text(book, "Adiós tengo un perro.", 2)
    db.session.add(book)
    db.session.commit()

    # Add terms
    add_terms(spanish, ["gato", "perro", "amigo"])
    db.session.commit()

    # Test entire book filter
    _dt_params["filtBook"] = f"{book.id}"
    _dt_params["filtBookScope"] = "all"
    d = get_data_tables_list(_dt_params, db.session)
    terms = [t["WoText"] for t in d["data"]]
    assert "gato" in terms
    assert "perro" in terms
    assert "amigo" not in terms

    # Test page 1 filter
    _dt_params["filtBookScope"] = "page"
    _dt_params["filtPageNum"] = "1"
    d = get_data_tables_list(_dt_params, db.session)
    terms = [t["WoText"] for t in d["data"]]
    assert "gato" in terms
    assert "perro" not in terms
    assert "amigo" not in terms

    # Test page 2 filter
    _dt_params["filtPageNum"] = "2"
    d = get_data_tables_list(_dt_params, db.session)
    terms = [t["WoText"] for t in d["data"]]
    assert "gato" not in terms
    assert "perro" in terms
    assert "amigo" not in terms
