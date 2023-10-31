"""
Db management.
"""

from sqlalchemy import text
from lute.db import db


def delete_all_data():
    """
    DANGEROUS!  Delete everything, null out settings.

    NO CHECKS ARE PERFORMED.
    """

    # Setting the pragma first ensures cascade delete.
    statements = [
        'pragma foreign_keys = ON',
        'delete from languages',
        'delete from tags',
        'delete from tags2',
        'update settings set StValue = null',
    ]
    for s in statements:
        db.session.execute(text(s))
    db.session.commit()
