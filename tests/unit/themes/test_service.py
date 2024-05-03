"""
Theme service tests.
"""

import os
import lute.themes.service as svc
from lute.db import db
from lute.models.setting import UserSetting


def test_list_themes(app_context):
    "Smoke test only."
    lst = svc.list_themes()
    assert len(lst) > 0, "have themes"
    assert lst[0][0] == "-", "No theme"
    assert lst[0][1] == "(default)"

    assert ("Apple_Books.css", "Apple Books") in lst


def test_default_theme_is_blank_css(app_context):
    "UserSetting starts off with blank css."
    assert UserSetting.get_value("current_theme") == "-"
    assert svc.get_current_css() == "", "Default = empty string."


def test_bad_setting_returns_blank_css(app_context):
    "Just in case."
    UserSetting.set_value("current_theme", "_missing_file.css")
    db.session.commit()
    assert svc.get_current_css() == "", "Missing = empty string."


def test_setting_a_theme_returns_its_css(app_context):
    "User choice is used."
    UserSetting.set_value("current_theme", "Apple_Books.css")
    db.session.commit()
    assert "Georgia" in svc.get_current_css(), "font specified"


def test_next_theme_cycles_themes(app_context):
    """
    Users should be able to move the 'next' theme quickly
    while reading, via a hotkey.
    """
    lst = svc.list_themes()
    assert UserSetting.get_value("current_theme") == lst[0][0]
    svc.next_theme()
    assert UserSetting.get_value("current_theme") == lst[1][0]
    for _ in range(0, len(lst) + 10):  # pylint: disable=consider-using-enumerate
        svc.next_theme()
        svc.next_theme()
    # OK


def _delete_custom_theme_files(theme_dir):
    "Delete custom file."
    for filename in os.listdir(theme_dir):
        filepath = os.path.join(theme_dir, filename)
        if os.path.isfile(filepath):
            os.remove(filepath)


def test_custom_theme_in_theme_dir_is_available(app, app_context):
    "Can use .css file in theme dir."
    theme_dir = app.env_config.userthemespath
    _delete_custom_theme_files(theme_dir)

    mytheme_content = "p { font-size: 30pt; }"
    themefile = os.path.join(theme_dir, "my_theme.css")
    with open(themefile, "w", encoding="utf-8") as f:
        f.write(mytheme_content)

    lst = svc.list_themes()
    assert ("my_theme.css", "my theme") in lst, "Have my theme"

    UserSetting.set_value("current_theme", "my_theme.css")
    db.session.commit()
    assert mytheme_content in svc.get_current_css(), "my theme used"


def test_custom_theme_in_theme_dir_appends_to_existing_theme(app, app_context):
    "Can use .css file in theme dir."
    theme_dir = app.env_config.userthemespath
    _delete_custom_theme_files(theme_dir)

    lst = svc.list_themes()
    assert ("Apple_Books.css", "Apple Books") in lst
    UserSetting.set_value("current_theme", "Apple_Books.css")
    db.session.commit()
    old_content = svc.get_current_css()

    mytheme_content = "p { font-size: 30pt; }"
    themefile = os.path.join(theme_dir, "Apple_Books.css")
    with open(themefile, "w", encoding="utf-8") as f:
        f.write(mytheme_content)

    lst = svc.list_themes()
    assert ("Apple_Books.css", "Apple Books") in lst, "Have my theme"

    UserSetting.set_value("current_theme", "Apple_Books.css")
    db.session.commit()

    new_css = old_content + "\n\n/* Additional user css */\n\n" + mytheme_content
    new_content = svc.get_current_css()
    assert new_css in new_content, "my theme used in addition to built-in"
