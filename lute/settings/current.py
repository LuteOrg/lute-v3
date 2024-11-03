"""
Current user settings stored in UserSettings.

Storing a global dict to allow for db-less access, they're
global settings, after all.

They're written to at load (or when the settings change).
"""

import os
from lute.models.setting import UserSetting, UserSettingRepository

# The current user settings, key/value dict.
current_settings = {}


def _revised_mecab_path(repo):
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

    mp = repo.get_value("mecab_path")
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


def load(session, default_user_backup_path):
    """
    Load missing user settings with default values.
    """
    repo = UserSettingRepository(session)

    # These keys are rendered into the global javascript namespace var
    # LUTE_USER_SETTINGS, so if any of these keys change, check the usage
    # of that variable as well.
    keys_and_defaults = {
        "backup_enabled": True,
        "backup_auto": True,
        "backup_warn": True,
        "backup_dir": default_user_backup_path,
        "backup_count": 5,
        "lastbackup": None,
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
        if not repo.key_exists(k):
            s = UserSetting()
            s.key = k
            s.value = v
            session.add(s)
    session.commit()

    # Revise the mecab path if necessary.
    # Note this is done _after_ the defaults are loaded,
    # because the user may have already loaded the defaults
    # (e.g. on machine upgrade) and stored them in the db,
    # so we may have to _update_ the existing setting.
    revised_mecab_path = _revised_mecab_path(repo)
    repo.set_value("mecab_path", revised_mecab_path)
    session.commit()

    refresh_global_settings(session)


def refresh_global_settings(session):
    "Refresh all settings dictionary."
    # Have to reload to not mess up any references
    # (e.g. during testing).
    current_settings.clear()

    settings = session.query(UserSetting).all()
    for s in settings:
        current_settings[s.key] = s.value

    # Convert some ints into bools.
    boolkeys = [
        "open_popup_in_new_tab",
        "stop_audio_on_term_form_open",
        "show_highlights",
    ]
    for k in boolkeys:
        current_settings[k] = current_settings[k] == "1"
