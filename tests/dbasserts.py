"""Database assertions.

This module is "registered" to pytest in ./__init__.py
to get nicer assertion details.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.sql import text

from lute.config.app_config import AppConfig


def __sqlite_uri():
    """
    Get the application Sqlite URL from the config file.
    """
    this_files_dir = os.path.dirname(os.path.realpath(__file__))
    conf_file = os.path.normpath(
        os.path.join(this_files_dir, "..", "lute", "config", "config.yml")
    )
    ac = AppConfig(conf_file)
    return ac.sqliteconnstring


def assert_sql_result(sql, expected, msg=""):
    """
    Checks sql results (stringized) against expected.

    e.g. with sql = "select 1, 2", expected would be [ "1; 2" ]

    This replaces all zero-width strings with '/'
    """
    uri = __sqlite_uri()
    engine = create_engine(uri)
    conn = engine.connect()
    result = conn.execute(text(sql))
    zws = "\u200B"  # zero-width space
    actual = ["; ".join([f"{s}".replace(zws, "/") for s in row]) for row in result]
    assert actual == expected, msg


def assert_record_count_equals(sql, expected, message=""):
    """
    Checks count of records of sql results (stringized) against expected.

    e.g. with sql = "select 1, 2", expected would be 1
    """

    uri = __sqlite_uri()
    engine = create_engine(uri)
    conn = engine.connect()

    # Check if the SQL query is a SELECT statement
    if not sql.lower().startswith("select"):
        sql = f"SELECT * FROM {sql}"

    query = text(sql)
    result = conn.execute(query)

    actual = ["; ".join([f"{s}" for s in row]) for row in result]

    if len(actual) != expected:
        message += f" ... got data:\n\n{actual}\n"

    assert len(actual) == expected, message
