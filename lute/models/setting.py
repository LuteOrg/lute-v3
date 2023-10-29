"""
Lute settings, in settings key-value table.
"""

from lute.db import db

class Setting(db.Model):
    "Settings table."
    __tablename__ = 'settings'
    key = db.Column('StKey', db.String(40), primary_key=True)
    value = db.Column('StValue', db.String(40), nullable=False)


    @staticmethod
    def set_key(keyname, keyvalue):
        "Set, but don't save, a setting."
        s = db.session.query(Setting).filter(Setting.key == keyname).first()
        if s is None:
            s = Setting()
            s.key = keyname
        s.value = keyvalue
        db.session.add(s)


    @staticmethod
    def get_key(keyname):
        "Get the saved key, or None if it doesn't exist."
        s = db.session.query(Setting).filter(Setting.key == keyname).first()
        if s is None:
            return None
        return s.value


    # Helpers for certain settings.

    @classmethod
    def get_last_backup_datetime(cls):
        "Get the last_backup_datetime as int, or None."
        v = Setting.get_key('lastbackup')
        if v is None:
            return None
        return int(v)

    @classmethod
    def set_last_backup_datetime(cls, v):
        "Set and save the last backup time."
        Setting.set_key('lastbackup', v)
        db.session.commit()
