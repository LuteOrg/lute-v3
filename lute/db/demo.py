"""
Functions to manage demo database.

Lute db comes pre-loaded with some demo data.  User can view Tutorial,
wipe data, etc.

The db settings table contains a record, StKey = 'IsDemoData', if the
data is demo.
"""

from sqlalchemy import text
from lute.db import db


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


def delete_all_data():
    """
    Deletes all the data, but throws if IsDemoData is not set.
    """
    if not contains_demo_data():
        raise RuntimeError("Can't delete non-demo data.")

    # Setting the pragma first ensures cascade delete.
    statements = [
        'pragma foreign_keys = ON',
        'delete from languages',
        'delete from settings',
        'delete from tags',
        'delete from tags2',
    ]
    for s in statements:
        db.session.execute(text(s))
    db.session.commit()
