"""
Book tests.
"""

from datetime import datetime
import pytest
from lute.models.language import Language
from lute.book.datatables import get_data_tables_list
from lute.db import db
from lute.db.demo import load_demo_stories
from tests.utils import make_book


@pytest.fixture(name="_dt_params")
def fixture_dt_params():
    "Sample query params."
    columns = [
        {"data": "0", "name": "BkID", "searchable": False, "orderable": False},
        {"data": "1", "name": "BkTitle", "searchable": True, "orderable": True},
        {"data": "2", "name": "IsCompleted", "searchable": False, "orderable": False},
    ]
    params = {
        "draw": "1",
        "columns": columns,
        "order": [{"column": "1", "dir": "asc"}],
        "start": "0",  # Start from page 0
        "length": "10",
        "search": {"value": "", "regex": False},
        "filtLanguage": "0",  # Ha!
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


def test_book_data_says_completed_if_last_page_has_been_read(
    app_context, _dt_params, english
):
    "Add a visual cue to completed books."
    b = make_book("title", "Hello.", english)
    db.session.add(b)
    db.session.commit()
    _dt_params["search"] = {"value": "title", "regex": False}
    d = get_data_tables_list(_dt_params, False)
    actual = d["data"][0]
    assert actual == [b.id, "title", 0], "not completed"
    t = b.texts[0]
    t.read_date = datetime.now()
    db.session.add(t)
    db.session.commit()
    d = get_data_tables_list(_dt_params, False)
    actual = d["data"][0]
    assert actual == [b.id, "title", 1], "completed"
