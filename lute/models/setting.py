"""
Lute settings, in settings key-value table.
"""

import os
import datetime
import time
from flask import current_app
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

    def set_value_post(self, keyname, keyvalue):
        """
        Post-setting value for certain keys."
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
        self.set_value_post(keyname, keyvalue)

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

    def set_value_post(self, keyname, keyvalue):
        """
        Setting some keys runs other code.
        """
        if keyname == "mecab_path":
            mp = "MECAB_PATH"
            if keyvalue is None or keyvalue == "":
                if mp in os.environ:
                    del os.environ[mp]
            else:
                os.environ[mp] = keyvalue.strip()

    def _revised_mecab_path(self):
        """
        Change the mecab_path if it's not found, and a
        replacement is found.

        Lute Docker images are built to be multi-arch, and
        interestingly (annoyingly), mecab libraries are installed into
        different locations depending on the architecture, even with
        the same Dockerfile and base image.

        Returns: new mecab path if old one is missing _and_
        new one found, otherwise just return the old one.
        """

        mp = self.get_value("mecab_path")
        if mp is not None and os.path.exists(mp):
            return mp

        # See develop docs for notes on how to find the libmecab path!
        candidates = [
            # linux/arm64
            "/lib/aarch64-linux-gnu/libmecab.so.2",
            # linux/amd64
            "/lib/x86_64-linux-gnu/libmecab.so.2",
            # github CI, ubuntu-latest
            "/lib/x86_64-linux-gnu/libmecab.so.2",
        ]
        replacements = [p for p in candidates if os.path.exists(p)]
        if len(replacements) > 0:
            return replacements[0]
        # Replacement not found, leave current value as-is.
        return mp

    def load(self):
        """
        Load missing user settings with default values.
        """
        app_config = current_app.env_config

        # These keys are rendered into the global javascript namespace var
        # LUTE_USER_SETTINGS, so if any of these keys change, check the usage
        # of that variable as well.
        keys_and_defaults = {
            "backup_enabled": True,
            "backup_auto": True,
            "backup_warn": True,
            "backup_dir": app_config.default_user_backup_path,
            "backup_count": 5,
            "mecab_path": None,
            "japanese_reading": "hiragana",
            "current_theme": "-",
            "custom_styles": "/* Custom css to modify Lute's appearance. */",
            "show_highlights": True,
            "current_language_id": 0,
            # Behaviour:
            "open_popup_in_new_tab": False,
            "stop_audio_on_term_form_open": True,
            "stats_calc_sample_size": 5,
            # Keyboard shortcuts.  These have default values assigned
            # as they were the hotkeys defined in the initial Lute
            # release.
            "hotkey_StartHover": "escape",
            "hotkey_PrevWord": "arrowleft",
            "hotkey_NextWord": "arrowright",
            "hotkey_StatusUp": "arrowup",
            "hotkey_StatusDown": "arrowdown",
            "hotkey_Bookmark": "b",
            "hotkey_CopySentence": "c",
            "hotkey_CopyPara": "shift+c",
            "hotkey_TranslateSentence": "t",
            "hotkey_TranslatePara": "shift+t",
            "hotkey_NextTheme": "m",
            "hotkey_ToggleHighlight": "h",
            "hotkey_ToggleFocus": "f",
            "hotkey_Status1": "1",
            "hotkey_Status2": "2",
            "hotkey_Status3": "3",
            "hotkey_Status4": "4",
            "hotkey_Status5": "5",
            "hotkey_StatusIgnore": "i",
            "hotkey_StatusWellKnown": "w",
            # New hotkeys.  These must have empty values, because
            # users may have already setup their hotkeys, and we can't
            # assume that a given key combination is free:
            "hotkey_CopyPage": "",
            "hotkey_DeleteTerm": "",
            "hotkey_EditPage": "",
            "hotkey_TranslatePage": "",
            "hotkey_PrevUnknownWord": "",
            "hotkey_NextUnknownWord": "",
            "hotkey_PrevSentence": "",
            "hotkey_NextSentence": "",
        }
        for k, v in keys_and_defaults.items():
            if not self.key_exists(k):
                s = UserSetting()
                s.key = k
                s.value = v
                self.session.add(s)
        self.session.commit()

        # Revise the mecab path if necessary.
        # Note this is done _after_ the defaults are loaded,
        # because the user may have already loaded the defaults
        # (e.g. on machine upgrade) and stored them in the db,
        # so we may have to _update_ the existing setting.
        revised_mecab_path = self._revised_mecab_path()
        self.set_value("mecab_path", revised_mecab_path)
        self.session.commit()

    def all_settings(self):
        """
        Get dict of all settings, for rendering into Javascript global space.
        """
        settings = self.session.query(UserSetting).all()
        ret = {}
        for s in settings:
            ret[s.key] = s.value

        # Convert some ints into bools.
        boolkeys = ["open_popup_in_new_tab", "stop_audio_on_term_form_open"]
        for k in boolkeys:
            ret[k] = ret[k] == "1"

        return ret


class SystemSetting(SettingBase):
    "System setting."
    __tablename__ = None
    __mapper_args__ = {"polymorphic_identity": "system"}

    # Helpers for certain sys settings.


class SystemSettingRepository(SettingRepositoryBase):
    "Repository."

    def __init__(self, session):
        super().__init__(session, SystemSetting)

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


class BackupSettings:
    """
    Convenience wrapper for current backup settings.
    Getter only.
    """

    def __init__(self, session):
        us_repo = UserSettingRepository(session)
        ss_repo = SystemSettingRepository(session)

        def _bool(k):
            v = us_repo.get_value(k)
            return v in (1, "1", "y", True)

        self.backup_enabled = _bool("backup_enabled")
        self.backup_auto = _bool("backup_auto")
        self.backup_warn = _bool("backup_warn")
        self.backup_dir = us_repo.get_value("backup_dir")
        self.backup_count = int(us_repo.get_value("backup_count") or 5)
        self.last_backup_datetime = ss_repo.get_last_backup_datetime()

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
