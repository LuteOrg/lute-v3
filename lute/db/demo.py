"""
Functions to manage demo database.

Lute db comes pre-loaded with some demo data.  User can view Tutorial,
wipe data, etc.

The db settings table contains a record, StKey = 'IsDemoData', if the
data is demo.
"""

from sqlalchemy import text
from lute.db import db
import lute.db.management


def contains_demo_data():
    """
    True if IsDemoData setting is present.
    """
    sql = "select StKey from settings where StKey = 'IsDemoData'"
    result = db.session.execute(text(sql)).fetchone()
    if result is None:
        return False
    return True


def remove_flag():
    """
    Remove IsDemoData setting.
    """
    sql = "delete from settings where StKey = 'IsDemoData'"
    db.session.execute(text(sql))
    db.session.commit()


def tutorial_book_id():
    """
    Return the book id of the tutorial.
    """
    if not contains_demo_data():
        return None
    sql = """select BkID from books
    inner join languages on LgID = BkLgID
    where LgName = 'English' and BkTitle = 'Tutorial'
    """
    r = db.session.execute(text(sql)).first()
    if r is None:
        return None
    return int(r[0])


def delete_demo_data():
    """
    If this is a demo, wipe everything.
    """
    if not contains_demo_data():
        raise RuntimeError("Can't delete non-demo data.")
    remove_flag()
    lute.db.management.delete_all_data()
