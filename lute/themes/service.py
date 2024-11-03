"""
Theming service.

Themes are stored in the css folder, current theme in UserSetting.
"""

import os
from glob import glob
from flask import current_app
from lute.models.repositories import UserSettingRepository

default_entry = ("-", "(default)")


class Service:
    "Service."

    def __init__(self, session):
        self.session = session

    def _css_path(self):
        """
        Path to css in this folder.
        """
        thisdir = os.path.dirname(__file__)
        theme_dir = os.path.join(thisdir, "css")
        return os.path.abspath(theme_dir)

    def list_themes(self):
        """
        List of theme file names and user-readable name.
        """

        def _make_display_name(s):
            ret = os.path.basename(s)
            ret = ret.replace(".css", "").replace("_", " ")
            return ret

        g = glob(os.path.join(self._css_path(), "*.css"))
        themes = [(os.path.basename(f), _make_display_name(f)) for f in g]
        theme_basenames = [t[0] for t in themes]

        g = glob(os.path.join(current_app.env_config.userthemespath, "*.css"))
        additional_user_themes = [
            (os.path.basename(f), _make_display_name(f))
            for f in g
            if os.path.basename(f) not in theme_basenames
        ]

        themes += additional_user_themes
        sorted_themes = sorted(themes, key=lambda x: x[1])
        return [default_entry] + sorted_themes

    def get_current_css(self):
        """
        Return the current css pointed at by the current_theme user setting.
        """
        repo = UserSettingRepository(self.session)
        current_theme = repo.get_value("current_theme")
        if current_theme == default_entry[0]:
            return ""

        def _get_theme_css_in_dir(d):
            "Get css, or '' if no file."
            fname = os.path.join(d, current_theme)
            if not os.path.exists(fname):
                return ""
            with open(fname, "r", encoding="utf-8") as f:
                return f.read()

        ret = _get_theme_css_in_dir(self._css_path())
        add = _get_theme_css_in_dir(current_app.env_config.userthemespath)
        if add != "":
            ret += f"\n\n/* Additional user css */\n\n{add}"
        return ret

    def next_theme(self):
        """
        Move to the next theme in the list of themes.
        """
        repo = UserSettingRepository(self.session)
        current_theme = repo.get_value("current_theme")
        themes = [t[0] for t in self.list_themes()]
        themes.append(default_entry[0])
        for i in range(0, len(themes)):  # pylint: disable=consider-using-enumerate
            if themes[i] == current_theme:
                new_index = i + 1
                break
        repo.set_value("current_theme", themes[new_index])
        self.session.commit()
