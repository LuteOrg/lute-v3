"""
Current user settings stored in UserSettings.

Storing a global dict to allow for db-less access, they're
global settings, after all.

They're written to at load (or when the settings change).
"""

from lute.models.setting import UserSetting

# The current user settings, key/value dict.
current_settings = {}

# Current user hotkey mappings, mapping to mapping_name dict.
current_hotkeys = {}


def refresh_global_settings(session):
    "Refresh all settings dictionary."
    # Have to reload to not mess up any references
    # (e.g. during testing).
    current_settings.clear()
    current_hotkeys.clear()

    settings = session.query(UserSetting).all()
    for s in settings:
        current_settings[s.key] = s.value

    hotkeys = [
        s for s in settings if s.key.startswith("hotkey_") and (s.value or "") != ""
    ]
    for h in hotkeys:
        current_hotkeys[h.value] = h.key

    # Convert some ints into bools.
    boolkeys = [
        "open_popup_in_new_tab",
        "stop_audio_on_term_form_open",
        "show_highlights",
        "term_popup_promote_parent_translation",
        "term_popup_show_components",
    ]
    for k in boolkeys:
        current_settings[k] = current_settings[k] == "1"
