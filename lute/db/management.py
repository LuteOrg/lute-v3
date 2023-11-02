"""
Db management.
"""

from sqlalchemy import text
from lute.db import db
from lute.models.setting import UserSetting, SystemSetting


def delete_all_data():
    """
    DANGEROUS!  Delete everything, null user settings, clear sys settings.

    NO CHECKS ARE PERFORMED.
    """

    # Setting the pragma first ensures cascade delete.
    statements = [
        'pragma foreign_keys = ON',
        'delete from languages',
        'delete from tags',
        'delete from tags2'
    ]
    for s in statements:
        db.session.execute(text(s))
    db.session.commit()

    for u in db.session.query(UserSetting).all():
        u.value = None
        db.session.add(u)
    for ss in db.session.query(SystemSetting).all():
        db.session.delete(ss)
    db.session.commit()
