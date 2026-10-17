"""
Single source of truth for user settings: their types and default values.

Historically the default values lived in
``lute.db.management.add_default_user_settings`` while the list of keys to
coerce to booleans lived separately in
``lute.settings.current.refresh_global_settings``.  Keeping the two in sync
by hand was error prone: a bool default could be added without adding it to
the coercion list, and there was a risk of coercing an integer setting (e.g.
``backup_count``) to a bool.

Both consumers now derive from ``USER_SETTING_DEFINITIONS`` below, which
records each key's type alongside its default value.

Note: these keys are rendered into the global javascript namespace var
``LUTE_USER_SETTINGS``, so if any key changes, check the usage of that
variable as well.
"""

# Each entry maps a user setting key to its type and default value.
#   type is one of "bool", "int", "str".
# The backup_dir default is machine-specific and supplied at load time (see
# user_setting_defaults), so its default here is None.
USER_SETTING_DEFINITIONS = {
    "backup_enabled": {"type": "bool", "value": True},
    "backup_auto": {"type": "bool", "value": True},
    "backup_warn": {"type": "bool", "value": True},
    "backup_dir": {"type": "str", "value": None},
    "backup_count": {"type": "int", "value": 5},
    "lastbackup": {"type": "str", "value": None},
    "mecab_path": {"type": "str", "value": None},
    "japanese_reading": {"type": "str", "value": "hiragana"},
    "current_theme": {"type": "str", "value": "-"},
    "custom_styles": {
        "type": "str",
        "value": "/* Custom css to modify Lute's appearance. */",
    },
    "show_highlights": {"type": "bool", "value": True},
    "current_language_id": {"type": "int", "value": 0},
    # Behaviour:
    "open_popup_in_new_tab": {"type": "bool", "value": False},
    "stop_audio_on_term_form_open": {"type": "bool", "value": True},
    "show_streak_on_home": {"type": "bool", "value": False},
    "stats_calc_sample_size": {"type": "int", "value": 5},
    # Term popups:
    "term_popup_promote_parent_translation": {"type": "bool", "value": True},
    "term_popup_show_components": {"type": "bool", "value": True},
    # Anki:
    "use_ankiconnect": {"type": "bool", "value": False},
    "ankiconnect_url": {"type": "str", "value": "http://127.0.0.1:8765"},
}


def user_setting_defaults(default_user_backup_path):
    "Key-to-default-value map, with backup_dir set to the given path."
    ret = {k: d["value"] for k, d in USER_SETTING_DEFINITIONS.items()}
    ret["backup_dir"] = default_user_backup_path
    return ret


def bool_setting_keys():
    "Keys whose stored string value should be coerced to a bool."
    return [k for k, d in USER_SETTING_DEFINITIONS.items() if d["type"] == "bool"]
