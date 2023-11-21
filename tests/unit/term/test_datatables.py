"""
Book tests.
"""

import pytest
from lute.term.datatables import get_data_tables_list


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
        "start": "1",
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
        "filtStatusMax": "0",
        "filtIncludeIgnored": "false",
    }
    return params


def test_smoke_term_datatables_query_runs(app_context, _dt_params):
    """
    Smoke test only, ensure query runs.
    """
    get_data_tables_list(_dt_params)
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
    get_data_tables_list(_dt_params)
