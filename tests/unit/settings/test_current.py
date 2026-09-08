"""
Current settings tests.
"""

from lute.db import db
from lute.settings.current import (
    refresh_global_settings,
    current_settings,
    current_hotkeys,
)


def test_refresh_refreshes_current_settings(app_context):
    "Current settings are loaded."
    if "backup_dir" in current_settings:
        del current_settings["backup_dir"]
    refresh_global_settings(db.session)
    assert "backup_dir" in current_settings, "loaded"


def test_hotkey_strings_mapped_to_name(app_context):
    "Hotkey key combo to name."
    refresh_global_settings(db.session)
    hotkey_names = current_hotkeys.values()
    assert "hotkey_Status5" in hotkey_names, "this is set by default"
    assert current_hotkeys["Digit5"] == "hotkey_Status5", "mapped"
    assert "" not in current_hotkeys, "No blank keyboard shortcuts"


def test_bool_settings_coerced_and_ints_left_alone(app_context):
    "Boolean settings become real bools; integer settings are not coerced."
    refresh_global_settings(db.session)

    # Boolean-typed settings are real bools, not the stored "1"/"0" strings.
    assert current_settings["show_highlights"] is True
    assert current_settings["open_popup_in_new_tab"] is False
    # Backup flags are bool-typed too, and now coerced consistently.
    assert current_settings["backup_enabled"] is True

    # Integer-typed settings must NOT be coerced to bools.
    assert not isinstance(current_settings["backup_count"], bool)
    assert not isinstance(current_settings["stats_calc_sample_size"], bool)
