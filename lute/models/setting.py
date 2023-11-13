"""
Lute settings, in settings key-value table.
"""

import datetime
from lute.db import db
from lute.parse.mecab_parser import JapaneseParser
from lute.config.app_config import AppConfig


class SettingBase(db.Model):
    """
    Main settings table.

    This class should not be used, it's the polymorphic base
    for UserSettings and SystemSettings.
    """

    __tablename__ = "settings"
    key = db.Column("StKey", db.String(40), primary_key=True)
    keytype = db.Column("StKeyType", db.String(10), nullable=False)
    value = db.Column("StValue", db.String, nullable=False)
    __mapper_args__ = {"polymorphic_on": keytype}

    @classmethod
    def key_exists_precheck(cls, keyname):
        """
        Check key validity for certain actions.
        """

    @classmethod
    def set_value(cls, keyname, keyvalue):
        "Set, but don't save, a setting."
        cls.key_exists_precheck(keyname)
        s = db.session.query(cls).filter(cls.key == keyname).first()
        if s is None:
            s = cls()
            s.key = keyname
        s.value = keyvalue
        db.session.add(s)

    @classmethod
    def key_exists(cls, keyname):
        "True if exists."
        s = db.session.query(cls).filter(cls.key == keyname).first()
        no_key = s is None
        return not no_key

    @classmethod
    def get_value(cls, keyname):
        "Get the saved key, or None if it doesn't exist."
        cls.key_exists_precheck(keyname)
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


class MissingUserSettingKeyException(Exception):
    """
    Cannot set or get unknown user keys.
    """


class UserSetting(SettingBase):
    "User setting."
    __tablename__ = None
    __mapper_args__ = {"polymorphic_identity": "user"}

    @classmethod
    def key_exists_precheck(cls, keyname):
        """
        User keys must exist.
        """
        if not UserSetting.key_exists(keyname):
            raise MissingUserSettingKeyException(keyname)

    @staticmethod
    def load():
        """
        Load missing user settings with default values.
        """
        app_config = AppConfig.create_from_config()

        keys_and_defaults = {
            "backup_enabled": True,
            "backup_auto": True,
            "backup_warn": True,
            "backup_dir": app_config.backup_path,
            "backup_count": 5,
            "mecab_path": app_config.mecab_path,
            "custom_styles": "/* Custom css to modify Lute's appearance. */",
        }
        for k, v in keys_and_defaults.items():
            if not UserSetting.key_exists(k):
                s = UserSetting()
                s.key = k
                s.value = v
                db.session.add(s)
        db.session.commit()

        # This feels wrong, somehow ... possibly could have an event
        # bus that posts messages about the setting.
        JapaneseParser.set_mecab_path_envkey(UserSetting.get_value("mecab_path"))


class SystemSetting(SettingBase):
    "System setting."
    __tablename__ = None
    __mapper_args__ = {"polymorphic_identity": "system"}

    # Helpers for certain sys settings.

    @classmethod
    def get_last_backup_datetime(cls):
        "Get the last_backup_datetime as int, or None."
        v = cls.get_value("lastbackup")
        if v is None:
            return None
        return int(v)

    @classmethod
    def set_last_backup_datetime(cls, v):
        "Set and save the last backup time."
        cls.set_value("lastbackup", v)
        db.session.commit()


class BackupSettings:
    """
    Convenience wrapper for current backup settings.
    Getter only.
    """

    def __init__(self):
        def _bool(k):
            v = UserSetting.get_value(k)
            return v in (1, "1", "y", True)

        self.backup_enabled = _bool("backup_enabled")
        self.backup_auto = _bool("backup_auto")
        self.backup_warn = _bool("backup_warn")
        self.backup_dir = UserSetting.get_value("backup_dir")
        self.backup_count = int(UserSetting.get_value("backup_count") or 5)
        self.last_backup_datetime = SystemSetting.get_last_backup_datetime()

    @property
    def last_backup_display_date(self):
        "Return the last_backup_datetime as yyyy-mm etc., or None if not set."
        t = self.last_backup_datetime
        if t is None:
            return None
        return datetime.datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def get_backup_settings():
        "Get BackupSettings."
        return BackupSettings()
