"""
Lute settings, in settings key-value table.
"""

import datetime
import time
from lute.db import db


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


class SettingRepositoryBase:
    "Repository."

    def __init__(self, session, classtype):
        self.session = session
        self.classtype = classtype

    def key_exists_precheck(self, keyname):
        """
        Check key validity for certain actions.
        """

    def set_value(self, keyname, keyvalue):
        "Set, but don't save, a setting."
        self.key_exists_precheck(keyname)
        s = (
            self.session.query(self.classtype)
            .filter(self.classtype.key == keyname)
            .first()
        )
        if s is None:
            s = self.classtype()
            s.key = keyname
        s.value = keyvalue
        self.session.add(s)

    def key_exists(self, keyname):
        "True if exists."
        s = (
            self.session.query(self.classtype)
            .filter(self.classtype.key == keyname)
            .first()
        )
        no_key = s is None
        return not no_key

    def get_value(self, keyname):
        "Get the saved key, or None if it doesn't exist."
        self.key_exists_precheck(keyname)
        s = (
            self.session.query(self.classtype)
            .filter(self.classtype.key == keyname)
            .first()
        )
        if s is None:
            return None
        return s.value

    def delete_key(self, keyname):
        "Delete a key."
        s = (
            self.session.query(self.classtype)
            .filter(self.classtype.key == keyname)
            .first()
        )
        if s is not None:
            self.session.delete(s)


class MissingUserSettingKeyException(Exception):
    """
    Cannot set or get unknown user keys.
    """


class UserSetting(SettingBase):
    "User setting."
    __tablename__ = None
    __mapper_args__ = {"polymorphic_identity": "user"}


class BackupSettings:
    """
    Convenience wrapper for current backup settings.
    Getter only.
    """

    def __init__(self):
        self.backup_enabled = None
        self.backup_auto = None
        self.backup_warn = None
        self.backup_dir = None
        self.backup_count = None
        self.last_backup_datetime = None

    @property
    def last_backup_display_date(self):
        "Return the last_backup_datetime as yyyy-mm etc., or None if not set."
        t = self.last_backup_datetime
        if t is None:
            return None
        return datetime.datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S")

    @property
    def time_since_last_backup(self):
        """
        Return the time since the last backup. Returns None either if not set or
        it is in the future.
        Eg. "3 days ago"
        """
        t = self.last_backup_datetime
        if t is None:
            return None

        delta = int(time.time() - t)
        if delta < 0:
            return None

        thresholds = [
            ("week", 1 * 60 * 60 * 24 * 7),
            ("day", 1 * 60 * 60 * 24),
            ("hour", 1 * 60 * 60),
            ("minute", 1 * 60),
            ("second", 1),
        ]

        for unit, seconds in thresholds:
            multiples = abs(delta // seconds)
            if multiples >= 1:
                message = f"{multiples} {unit}"
                if multiples > 1:
                    message += "s"
                break
        else:
            message = f"{abs(delta)} seconds"

        return message + " ago"


class UserSettingRepository(SettingRepositoryBase):
    "Repository."

    def __init__(self, session):
        super().__init__(session, UserSetting)

    def key_exists_precheck(self, keyname):
        """
        User keys must exist.
        """
        if not self.key_exists(keyname):
            raise MissingUserSettingKeyException(keyname)

    def get_backup_settings(self):
        "Convenience method."
        bs = BackupSettings()

        def _bool(k):
            return self.get_value(k) in (1, "1", "y", True)

        bs.backup_enabled = _bool("backup_enabled")
        bs.backup_auto = _bool("backup_auto")
        bs.backup_warn = _bool("backup_warn")
        bs.backup_dir = self.get_value("backup_dir")
        bs.backup_count = int(self.get_value("backup_count") or 5)
        bs.last_backup_datetime = self.get_last_backup_datetime()
        return bs

    def get_last_backup_datetime(self):
        "Get the last_backup_datetime as int, or None."
        v = self.get_value("lastbackup")
        if v is None:
            return None
        return int(v)

    def set_last_backup_datetime(self, v):
        "Set and save the last backup time."
        self.set_value("lastbackup", v)
        self.session.commit()


class SystemSetting(SettingBase):
    "System setting."
    __tablename__ = None
    __mapper_args__ = {"polymorphic_identity": "system"}

    # Helpers for certain sys settings.


class SystemSettingRepository(SettingRepositoryBase):
    "Repository."

    def __init__(self, session):
        super().__init__(session, SystemSetting)
