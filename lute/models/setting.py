"""
Lute settings, in settings key-value table.
"""

from lute.db import db

class Setting(db.Model):
    "Settings table."
    key = db.Column('StKey', db.String(40), primary_key=True)
    value = db.Column('StValue', db.String(40), nullable=False)
