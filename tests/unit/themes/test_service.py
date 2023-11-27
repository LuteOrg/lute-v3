"""
Theme service tests.
"""

import lute.themes.service as svc
from lute.db import db
from lute.models.setting import UserSetting


def test_list_themes():
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
    for i in range(0, len(lst) + 10):  # pylint: disable=consider-using-enumerate
        print(i)
        svc.next_theme()
        svc.next_theme()
    # OK
