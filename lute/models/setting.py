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


class SystemSetting(SettingBase):
    "System setting."
    __tablename__ = None
    __mapper_args__ = {"polymorphic_identity": "system"}
