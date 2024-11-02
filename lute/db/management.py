"""
Db management.
"""

from sqlalchemy import text
from flask import current_app
from lute.settings.current import load


def delete_all_data(session):
    """
    DANGEROUS!  Delete everything, restore user settings, clear sys settings.

    NO CHECKS ARE PERFORMED.
    """

    # Setting the pragma first ensures cascade delete.
    statements = [
        "pragma foreign_keys = ON",
        "delete from languages",
        "delete from tags",
        "delete from tags2",
        "delete from settings",
    ]
    for s in statements:
        session.execute(text(s))
    session.commit()
    load(session, current_app.env_config.default_user_backup_path)
