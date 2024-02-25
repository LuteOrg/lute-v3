"""
Theming service.

Themes are stored in the css folder.  Current theme is saved in
UserSetting.
"""

import os
from glob import glob
from lute.models.setting import UserSetting
from lute.db import db

default_entry = ("-", "(default)")


def _css_path():
    """
    Path to css in this folder.
    """
    thisdir = os.path.dirname(__file__)
    theme_dir = os.path.join(thisdir, "css")
    return os.path.abspath(theme_dir)


def list_themes():
    """
    List of theme file names and user-readable name.
    """
    theme_glob = os.path.join(_css_path(), "*.css")

    def _make_display_name(s):
        ret = os.path.basename(s)
        ret = ret.replace(".css", "").replace("_", " ")
        return ret

    glob_results = glob(theme_glob)
    themes = [(os.path.basename(f), _make_display_name(f)) for f in glob_results]
    sorted_themes = sorted(themes, key=lambda x: x[1])
    return [default_entry] + sorted_themes


def get_current_css():
    """
    Return the current css pointed at by the current_theme user setting.
    """
    current_theme = UserSetting.get_value("current_theme")
    if current_theme == default_entry[0]:
        return ""
    theme_css = os.path.join(_css_path(), current_theme)
    if not os.path.exists(theme_css):
        # _Probably_ should raise an error here ...
        return ""
    with open(theme_css, "r", encoding="utf-8") as f:
        return f.read()


def next_theme():
    """
    Move to the next theme in the list of themes.
    """
    current_theme = UserSetting.get_value("current_theme")
    themes = [t[0] for t in list_themes()]
    themes.append(default_entry[0])
    for i in range(0, len(themes)):  # pylint: disable=consider-using-enumerate
        if themes[i] == current_theme:
            new_index = i + 1
            break
    UserSetting.set_value("current_theme", themes[new_index])
    db.session.commit()
