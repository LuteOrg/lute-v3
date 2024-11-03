"""
Current user settings stored in UserSettings.

Storing a global dict to allow for db-less access, they're
global settings, after all.

They're written to at load (or when the settings change).
"""

from lute.models.setting import UserSetting

# The current user settings, key/value dict.
current_settings = {}


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
