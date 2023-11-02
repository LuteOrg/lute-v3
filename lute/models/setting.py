"""
Lute settings, in settings key-value table.
"""

import datetime
from lute.db import db

class SettingBase(db.Model):
    """
    Main settings table.

    This class should not be used, it's the polymorphic base
    for UserSettings and SystemSettings.
    """
    __tablename__ = 'settings'
    key = db.Column('StKey', db.String(40), primary_key=True)
    keytype = db.Column('StKeyType', db.String(10), nullable=False)
    value = db.Column('StValue', db.String, nullable=False)
    __mapper_args__ = {"polymorphic_on": keytype}

    @classmethod
    def set_value(cls, keyname, keyvalue):
        "Set, but don't save, a setting."
        s = db.session.query(cls).filter(cls.key == keyname).first()
        if s is None:
            s = cls()
            s.key = keyname
        s.value = keyvalue
        db.session.add(s)


    @classmethod
    def get_value(cls, keyname):
        "Get the saved key, or None if it doesn't exist."
        s = db.session.query(cls).filter(cls.key == keyname).first()
        if s is None:
            return None
        return s.value

    @classmethod
    def delete_key(cls, keyname):
        "Delete a key."
        s = db.session.query(cls).filter(cls.key == keyname).first()
        if s is not None:
            db.session.delete(s)


class UserSetting(SettingBase):
    "User setting."
    __tablename__ = None
    __mapper_args__ = {"polymorphic_identity": 'user'}


class SystemSetting(SettingBase):
    "System setting."
    __tablename__ = None
    __mapper_args__ = {"polymorphic_identity": 'system'}

    # Helpers for certain sys settings.

    @classmethod
    def get_last_backup_datetime(cls):
        "Get the last_backup_datetime as int, or None."
        v = cls.get_value('lastbackup')
        if v is None:
            return None
        return int(v)

    @classmethod
    def set_last_backup_datetime(cls, v):
        "Set and save the last backup time."
        cls.set_value('lastbackup', v)
        db.session.commit()


class BackupSettings:
    """
    Convenience wrapper for current backup settings.
    Getter only.
    """
    def __init__(self):
        self.backup_enabled = UserSetting.get_value('backup_enabled')
        self.backup_dir = UserSetting.get_value('backup_dir')

        def _bool(k):
            v = UserSetting.get_value(k)
            return v in (1, '1', 'y', True)
        self.backup_auto = _bool('backup_auto')
        self.backup_warn = _bool('backup_warn')
        self.backup_count = int(UserSetting.get_value('backup_count') or 5)
        self.last_backup_datetime = SystemSetting.get_last_backup_datetime()

    def is_acknowledged(self):
        return self.backup_enabled in ('y', 'n')

    def last_backup_display_date(self):
        "Return the last_backup_datetime as yyyy-mm etc., or None if not set."
        t = self.last_backup_datetime
        if t is None:
            return None
        return datetime.datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M:%S')


    @staticmethod
    def get_backup_settings():
        "Get BackupSettings."
        return BackupSettings()
