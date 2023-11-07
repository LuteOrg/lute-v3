"""
Book tests.
"""

import pytest
from lute.models.language import Language
from lute.book.datatables import get_data_tables_list
from lute.db import db
from lute.db.demo import load_demo_stories


@pytest.fixture(name="_dt_params")
def fixture_dt_params():
    "Sample query params."
    columns = [
        {"data": "0", "name": "BkID", "searchable": False, "orderable": False},
        {"data": "1", "name": "BkTitle", "searchable": True, "orderable": True},
    ]
    params = {
        "draw": "1",
        "columns": columns,
        "order": [{"column": "1", "dir": "asc"}],
        "start": "1",
        "length": "10",
        "search": {"value": "", "regex": False},
    }
    return params


def test_smoke_book_datatables_query_runs(app_context, _dt_params):
    """
    Smoke test only, ensure query runs.
    """
    load_demo_stories()
    get_data_tables_list(_dt_params, False)
    # print(d['data'])
    a = 1
    assert a == 1, "dummy check"


def test_book_query_only_returns_supported_language_books(app_context, _dt_params):
    """
    Smoke test only, ensure query runs.
    """
    load_demo_stories()
    for lang in db.session.query(Language).all():
        lang.parser_type = "unknown"
        db.session.add(lang)
    db.session.commit()
    d = get_data_tables_list(_dt_params, False)
    assert len(d["data"]) == 0, "no books should be active"
