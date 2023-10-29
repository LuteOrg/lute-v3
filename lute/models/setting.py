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
    def set_value(keyname, keyvalue):
        "Set, but don't save, a setting."
        s = db.session.query(Setting).filter(Setting.key == keyname).first()
        if s is None:
            s = Setting()
            s.key = keyname
        s.value = keyvalue
        db.session.add(s)


    @staticmethod
    def get_value(keyname):
        "Get the saved key, or None if it doesn't exist."
        s = db.session.query(Setting).filter(Setting.key == keyname).first()
        if s is None:
            return None
        return s.value


    # Helpers for certain settings.

    @classmethod
    def get_last_backup_datetime(cls):
        "Get the last_backup_datetime as int, or None."
        v = Setting.get_value('lastbackup')
        if v is None:
            return None
        return int(v)

    @classmethod
    def set_last_backup_datetime(cls, v):
        "Set and save the last backup time."
        Setting.set_value('lastbackup', v)
        db.session.commit()


    class BackupSettings:
        """
        Convenience wrapper for current backup settings.
        Getter only.
        """
        def __init__(self):
            # -, y, or n
            self.backup_enabled = Setting.get_value('backup_enabled')
            self.backup_dir = Setting.get_value('backup_dir')

            def _bool(k):
                v = Setting.get_value(k)
                return v in (1, '1', 'y', True)
            self.backup_auto = _bool('backup_auto')
            self.backup_warn = _bool('backup_warn')
            self.backup_count = int(Setting.get_value('backup_count'))
            self.last_backup_datetime = Setting.get_last_backup_datetime()

        def is_acknowledged(self):
            return self.backup_enabled in ('y', 'n')


    @staticmethod
    def get_backup_settings():
        "Get BackupSettings."
        b = Setting.BackupSettings()
        return b
