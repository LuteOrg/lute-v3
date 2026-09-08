"""
Tests for the shared user-setting definitions.
"""

from lute.settings.setting_defaults import (
    USER_SETTING_DEFINITIONS,
    user_setting_defaults,
    bool_setting_keys,
)


def test_user_setting_defaults_fills_in_backup_dir():
    "backup_dir default is the supplied path; other defaults are unchanged."
    defaults = user_setting_defaults("/some/backup/path")
    assert defaults["backup_dir"] == "/some/backup/path"
    assert defaults["backup_count"] == 5
    assert defaults["ankiconnect_url"] == "http://127.0.0.1:8765"
    assert set(defaults.keys()) == set(USER_SETTING_DEFINITIONS.keys())


def test_bool_setting_keys_are_exactly_the_bool_typed_keys():
    "The bool key list is derived from the definitions' types."
    expected = {k for k, d in USER_SETTING_DEFINITIONS.items() if d["type"] == "bool"}
    assert set(bool_setting_keys()) == expected
    # Integer settings must not be included.
    assert "backup_count" not in bool_setting_keys()
    assert "stats_calc_sample_size" not in bool_setting_keys()
