"""
Current settings tests.
"""

from lute.db import db
from lute.settings.current import refresh_global_settings, current_settings


def test_refresh_refreshes_current_settings(app_context):
    "Current settigns are loaded."
    if "backup_dir" in current_settings:
        del current_settings["backup_dir"]
    refresh_global_settings(db.session)
    assert "backup_dir" in current_settings, "loaded"
