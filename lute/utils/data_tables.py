"""
Helper methods to get data for datatables display.
"""

import re
from sqlalchemy.sql import text
from lute.parse.registry import supported_parser_types


def supported_parser_type_criteria():
    "Helper to get all supported parser_types."
    typecrit = [f"'{p}'" for p in supported_parser_types()]
    typecrit.append("'zz_dummy_parser'")
    return ",".join(typecrit)


class DataTablesFlaskParamParser:
    """
    Parse datatables form parameters into the structure needed for
    DataTablesSqliteQuery.

    The standard datatables ajax post gives parameters like the following:

    draw: 1
    columns[0][data]: 0
    columns[0][name]: BkTitle
    columns[0][searchable]: true
    columns[0][orderable]: true

    Flask converts that to this, more or less:

    {
      draw: 1
      columns[0][data]: 0
      columns[0][name]: BkTitle
      columns[0][searchable]: true
      columns[0][orderable]: true
    }

    But the query helper requires parameters like this:

    {
      draw: 1,
      columns: [
        { data: 0, name: BkTitle, ... }
    }

    All code here adapted from https://github.com/coding-doc/
    sqlalchemy2-datatables/blob/main/src/datatables/datatable.py.
    """

    @staticmethod
    def _parse_order(request_params):
        """Parse the order[index][*] parameters."""
        order = []
        order_re = re.compile(r"order\[(.*?)]\[column]")
        order_params = {k: v for k, v in request_params.items() if order_re.match(k)}

        for i in range(len(order_params)):
            dt_column_order = {
                "column": int(request_params[f"order[{i}][column]"]),
                "dir": request_params[f"order[{i}][dir]"],
            }
            order.append(dt_column_order)
        return order

    @staticmethod
    def _parse_columns(request_params):
        """Parse the column[index][*] parameters."""
        columns = []
        # Extract only the keys of type columns[i][data] from the params
        data_re = re.compile(r"columns\[(.*?)]\[data]")
        data_param = {k: v for k, v in request_params.items() if data_re.match(k)}

        for i in range(len(data_param)):
            column = {
                "index": i,
                "data": data_param.get(f"columns[{i}][data]"),
                "name": request_params.get(f"columns[{i}][name]"),
                "searchable": request_params.get(f"columns[{i}][searchable]") == "true",
                "orderable": request_params.get(f"columns[{i}][orderable]") == "true",
                "search": {
                    "value": request_params.get(f"columns[{i}][search][value]"),
                    "regex": request_params.get(f"columns[{i}][search][regex]")
                    == "true",
                },
            }
            columns.append(column)
        return columns

    @staticmethod
    def parse_params(requestform) -> dict:
        """Parse the request (query) parameters."""
        request_params = requestform.to_dict(flat=True)

        return {
            "draw": int(request_params.get("draw", 1)),
            "start": int(request_params.get("start", 0)),
            "length": int(request_params.get("length", -1)),
            "search": {
                "value": request_params.get("search[value]"),
                "regex": request_params.get("search[regex]") == "true",
            },
            "columns": DataTablesFlaskParamParser._parse_columns(request_params),
            "order": DataTablesFlaskParamParser._parse_order(request_params),
        }


class DataTablesSqliteQuery:
    "Get data for datatables rendering."

    @staticmethod
    def where_and_params(searchable_cols, parameters):
        "Build where string and get the 'where' parameters."

        search = parameters["search"]
        search_string = search["value"] if search["value"] is not None else ""
        search_string = search_string.strip()

        search_parts = search_string.split()
        search_parts = list(filter(lambda p: len(p) > 0, search_parts))

        # If no searchable columns or search params, stop.
        if len(searchable_cols) == 0 or len(search_parts) == 0:
            return ["", {}]

        params = {}
        part_wheres = []
        for i, p in enumerate(search_parts):
            lwild = "%" if not p.startswith("^") else ""
            rwild = "%" if not p.endswith("$") else ""
            p = p.lstrip("^").rstrip("$")
            params[f"s{i}"] = p

            col_wheres = []
            for cname in searchable_cols:
                col_wheres.append(f"{cname} LIKE '{lwild}' || :s{i} || '{rwild}'")

            part_wheres.append("(" + " OR ".join(col_wheres) + ")")

        return ["WHERE " + " AND ".join(part_wheres), params]

    @staticmethod
    def get_sql(base_sql, parameters):
        "Build sql used for datatables queries."
        columns = parameters["columns"]

        def cols_with(attr):
            return [c["name"] for c in columns if c[attr] is True]

        orderby = ", ".join(cols_with("orderable"))
        for order in parameters["order"]:
            col_index = int(order["column"])
            sort_field = columns[col_index]["name"]
            orderby = f"{sort_field} {order['dir']}, {orderby}"
        orderby = f"ORDER BY {orderby}"

        [where, params] = DataTablesSqliteQuery.where_and_params(
            cols_with("searchable"), parameters
        )

        realbase = f"({base_sql}) realbase".replace("\n", " ")
        select_field_list = ", ".join([c["name"] for c in columns if c["name"] != ""])

        start = parameters["start"]
        length = parameters["length"]
        # pylint: disable=line-too-long
        data_sql = f"SELECT {select_field_list} FROM (select * from {realbase} {where} {orderby} LIMIT {start}, {length}) src {orderby}"

        return {
            "recordsTotal": f"select count(*) from {realbase}",
            "recordsFiltered": f"select count(*) from {realbase} {where}",
            "data": data_sql,
            "params": params,
            "draw": int(parameters["draw"]),
        }

    @staticmethod
    def get_data(base_sql, parameters, conn):
        "Return dict required for datatables rendering."
        recordsTotal = None
        recordsFiltered = None

        try:
            sql_dict = DataTablesSqliteQuery.get_sql(base_sql, parameters)

            def runqry(name, use_params=True):
                "Run the given query from the datatables list of queries."
                prms = None
                if use_params:
                    prms = sql_dict["params"]
                return conn.execute(text(sql_dict[name]), prms)

            recordsTotal = runqry("recordsTotal", False).fetchone()[0]
            recordsFiltered = runqry("recordsFiltered").fetchone()[0]
            res = runqry("data")
            ret = [list(row) for row in res.fetchall()]
        except Exception as e:
            raise e

        result = {
            "recordsTotal": recordsTotal,
            "recordsFiltered": recordsFiltered,
            "data": ret,
        }
        return result
