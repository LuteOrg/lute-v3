"""
Book tests.
"""

from lute.book.datatables import get_data_tables_list

def test_smoke_datatables_query_runs(app_context):
    """
    Smoke test only, ensure query runs.
    """
    columns = [
        {
            "data": "0",
            "name": "BkID",
            "searchable": False,
            "orderable": False
        },
        {
            "data": "1",
            "name": "BkTitle",
            "searchable": True,
            "orderable": True
        },
    ]
    params = {
        "draw": "1",
        "columns": columns,
        "order": [
            {
                "column": "1",
                "dir": "asc"
            }
        ],
        "start": "10",
        "length": "50",
        "search": {
            "value": "",
            "regex": False
        }
    }

    d = get_data_tables_list(params, False)
    print(d)
    a = 1
    assert a == 1, 'dummy check'
