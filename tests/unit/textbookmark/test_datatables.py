"""
TextBookmark DataTable tests.
"""

import pytest
from lute.bookmarks.datatables import get_data_tables_list


@pytest.fixture(name="_dt_params")
def fixture_dt_params():
    "Sample query params."
    columns = [
        {"data": "0", "name": "TxOrder", "searchable": True, "orderable": True},
        {"data": "1", "name": "TbTitle", "searchable": True, "orderable": True},
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


def test_smoke_term_datatables_query_runs(app_context, _dt_params):
    """
    Smoke test only, ensure query runs.
    """
    data = get_data_tables_list(_dt_params, 1)
    assert data is not None
