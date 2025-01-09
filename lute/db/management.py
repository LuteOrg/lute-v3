"""
Db management.
"""

import os
from sqlalchemy import text
from flask import current_app
from lute.models.setting import UserSetting
from lute.settings.hotkey_data import initial_hotkey_defaults
from lute.models.repositories import UserSettingRepository


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
    add_default_user_settings(session, current_app.env_config.default_user_backup_path)


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


def add_default_user_settings(session, default_user_backup_path):
    """
    Load missing user settings with default values.
    """
    repo = UserSettingRepository(session)

    def add_initial_vals_if_needed(hsh):
        "Add settings as required."
        for k, v in hsh.items():
            if not repo.key_exists(k):
                s = UserSetting()
                s.key = k
                s.value = v
                session.add(s)
        session.commit()

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
        # Term popups:
        "term_popup_promote_parent_translation": True,
        "term_popup_show_components": True,
    }
    add_initial_vals_if_needed(keys_and_defaults)

    # Revise the mecab path if necessary.
    # Note this is done _after_ the defaults are loaded,
    # because the user may have already loaded the defaults
    # (e.g. on machine upgrade) and stored them in the db,
    # so we may have to _update_ the existing setting.
    revised_mecab_path = _revised_mecab_path(repo)
    repo.set_value("mecab_path", revised_mecab_path)
    session.commit()

    add_initial_vals_if_needed(initial_hotkey_defaults())
