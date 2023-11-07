"""
DataTables sqlite tests.
"""

import re
import pytest
from lute.utils.data_tables import DataTablesSqliteQuery

# pylint: disable=line-too-long
# The tests all generate sql, which in most cases is quite long.


@pytest.fixture(name="basesql")
def fixture_basesql():
    "Base select for tests."
    return "select CatID, Color, Food from Cats"


@pytest.fixture(name="columns")
def fixture_columns():
    "Columns that would be returned from DataTablesFlaskParamParser."
    return [
        {"data": "0", "name": "CatID", "searchable": False, "orderable": False},
        {"data": "1", "name": "Color", "searchable": True, "orderable": True},
        {"data": "2", "name": "Food", "searchable": True, "orderable": True},
    ]


@pytest.fixture(name="parameters")
def fixture_parameters(columns):
    "Parameters that would be passed from DataTablesFlaskParamParser."
    return {
        "draw": "1",
        "columns": columns,
        "order": [{"column": "1", "dir": "asc"}],
        "start": "10",
        "length": "50",
        "search": {"value": "", "regex": False},
    }


def test_smoke_test(basesql, parameters):
    "Thing works when params are passed!"
    actual = DataTablesSqliteQuery.get_sql(basesql, parameters)
    expected = {
        "recordsTotal": "select count(*) from (select CatID, Color, Food from Cats) realbase",
        "recordsFiltered": "select count(*) from (select CatID, Color, Food from Cats) realbase ",
        "data": "SELECT CatID, Color, Food FROM (select * from (select CatID, Color, Food from Cats) realbase  ORDER BY Color asc, Color, Food LIMIT 10, 50) src ORDER BY Color asc, Color, Food",
        "params": {},
        "draw": 1,
    }
    assert actual == expected


def test_sorting(basesql, parameters):
    "Sorting is included in the data query."
    parameters["order"][0]["column"] = "2"
    parameters["order"][0]["dir"] = "desc"

    actual = DataTablesSqliteQuery.get_sql(basesql, parameters)
    expected = {
        "recordsTotal": "select count(*) from (select CatID, Color, Food from Cats) realbase",
        "recordsFiltered": "select count(*) from (select CatID, Color, Food from Cats) realbase ",
        "data": "SELECT CatID, Color, Food FROM (select * from (select CatID, Color, Food from Cats) realbase  ORDER BY Food desc, Color, Food LIMIT 10, 50) src ORDER BY Food desc, Color, Food",
        "params": {},
        "draw": 1,
    }
    assert actual == expected


def test_single_search(basesql, parameters):
    "A single search param is used in the where clause."
    parameters["search"]["value"] = "XXX"

    actual = DataTablesSqliteQuery.get_sql(basesql, parameters)

    expected = {
        "recordsTotal": "select count(*) from (select CatID, Color, Food from Cats) realbase",
        "recordsFiltered": "select count(*) from (select CatID, Color, Food from Cats) realbase WHERE (Color LIKE '%' || :s0 || '%' OR Food LIKE '%' || :s0 || '%')",
        "data": "SELECT CatID, Color, Food FROM (select * from (select CatID, Color, Food from Cats) realbase WHERE (Color LIKE '%' || :s0 || '%' OR Food LIKE '%' || :s0 || '%') ORDER BY Color asc, Color, Food LIMIT 10, 50) src ORDER BY Color asc, Color, Food",
        "params": {"s0": "XXX"},
        "draw": 1,
    }
    assert actual == expected


def test_multiple_search_terms(basesql, parameters):
    "Different search terms are used for all the searchable columns."
    parameters["search"]["value"] = "XXX YYY"

    actual = DataTablesSqliteQuery.get_sql(basesql, parameters)

    expected = {
        "recordsTotal": "select count(*) from (select CatID, Color, Food from Cats) realbase",
        "recordsFiltered": "select count(*) from (select CatID, Color, Food from Cats) realbase WHERE (Color LIKE '%' || :s0 || '%' OR Food LIKE '%' || :s0 || '%') AND (Color LIKE '%' || :s1 || '%' OR Food LIKE '%' || :s1 || '%')",
        "data": "SELECT CatID, Color, Food FROM (select * from (select CatID, Color, Food from Cats) realbase WHERE (Color LIKE '%' || :s0 || '%' OR Food LIKE '%' || :s0 || '%') AND (Color LIKE '%' || :s1 || '%' OR Food LIKE '%' || :s1 || '%') ORDER BY Color asc, Color, Food LIMIT 10, 50) src ORDER BY Color asc, Color, Food",
        "params": {"s0": "XXX", "s1": "YYY"},
        "draw": 1,
    }
    assert actual == expected


def test_search_regex_markers(basesql, parameters):
    "^ or $ has special meaning in the searches."

    def assert_where_equals(search_string, expected):
        parameters["search"]["value"] = search_string
        actual = DataTablesSqliteQuery.get_sql(basesql, parameters)
        filtered = actual["recordsFiltered"]
        where = re.sub(".* WHERE ", "", filtered)
        assert where == expected, search_string

    assert_where_equals(
        "XXX", "(Color LIKE '%' || :s0 || '%' OR Food LIKE '%' || :s0 || '%')"
    )
    assert_where_equals(
        "^XXX", "(Color LIKE '' || :s0 || '%' OR Food LIKE '' || :s0 || '%')"
    )
    assert_where_equals(
        "XXX$", "(Color LIKE '%' || :s0 || '' OR Food LIKE '%' || :s0 || '')"
    )
    assert_where_equals(
        "^XXX$", "(Color LIKE '' || :s0 || '' OR Food LIKE '' || :s0 || '')"
    )
