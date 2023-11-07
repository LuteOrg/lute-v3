"""
Book tests.
"""

from lute.termtag.datatables import get_data_tables_list


def test_smoke_datatables_query_runs(app_context):
    """
    Smoke test only, ensure query runs.
    """
    columns = [
        {"data": "0", "name": "TgID", "searchable": False, "orderable": False},
        {"data": "1", "name": "TgText", "searchable": True, "orderable": True},
    ]
    params = {
        "draw": "1",
        "columns": columns,
        "order": [{"column": "1", "dir": "asc"}],
        "start": "10",
        "length": "50",
        "search": {"value": "", "regex": False},
    }

    d = get_data_tables_list(params)
    print(d)
    a = 1
    assert a == 1, "dummy check"
