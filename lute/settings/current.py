"""
Current user settings stored in UserSettings.

Storing a global dict to allow for db-less access, they're
global settings, after all.

They're written to at load (or when the settings change).
"""

from lute.models.setting import UserSetting
from lute.settings.setting_defaults import bool_setting_keys

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

    # Convert stored string values of boolean settings into real bools.
    # The set of boolean keys comes from the shared setting definitions, so
    # integer settings are never accidentally coerced to bools.
    for k in bool_setting_keys():
        if k in current_settings:
            current_settings[k] = current_settings[k] == "1"
