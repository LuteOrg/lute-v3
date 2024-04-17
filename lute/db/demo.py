"""
Functions to manage demo database.

Lute db comes pre-loaded with some demo data.  User can view Tutorial,
wipe data, etc.

The db settings table contains a record, StKey = 'IsDemoData', if the
data is demo.
"""

import os
from glob import glob
import yaml
from sqlalchemy import text

from lute.models.language import Language
import lute.language.service
from lute.book.model import Repository
from lute.book.stats import refresh_stats
from lute.models.setting import SystemSetting
from lute.db import db
import lute.db.management


def _demo_languages():
    """
    Demo languages to be loaded for new users.
    Also loaded during tests.
    """
    return [
        "Arabic",
        "Classical Chinese",
        "Czech",
        "English",
        "French",
        "German",
        "Greek",
        "Hindi",
        "Japanese",
        "Russian",
        "Sanskrit",
        "Spanish",
        "Turkish",
    ]


def contains_demo_data():
    """
    True if IsDemoData setting is present.
    """
    ss = SystemSetting.get_value("IsDemoData")
    if ss is None:
        return False
    return True


def remove_flag():
    """
    Remove IsDemoData setting.
    """
    if not contains_demo_data():
        raise RuntimeError("Can't delete non-demo data.")

    SystemSetting.delete_key("IsDemoData")
    db.session.commit()


def tutorial_book_id():
    """
    Return the book id of the tutorial.
    """
    if not contains_demo_data():
        return None
    sql = """select BkID from books
    inner join languages on LgID = BkLgID
    where LgName = 'English' and BkTitle = 'Tutorial'
    """
    r = db.session.execute(text(sql)).first()
    if r is None:
        return None
    return int(r[0])


def delete_demo_data():
    """
    If this is a demo, wipe everything.
    """
    if not contains_demo_data():
        raise RuntimeError("Can't delete non-demo data.")
    remove_flag()
    lute.db.management.delete_all_data()


# Loading demo data.


def _demo_data_path():
    """
    Path to the demo data yaml files.
    """
    thisdir = os.path.dirname(__file__)
    demo_dir = os.path.join(thisdir, "language_defs")
    return os.path.abspath(demo_dir)


def _get_language_from_file(filename):
    """
    Create a new Language object from a yaml definition.
    """
    with open(filename, "r", encoding="utf-8") as file:
        d = yaml.safe_load(file)
        return Language.from_dict(d)


def predefined_languages():
    "Languages that have yaml files."
    demo_glob = os.path.join(_demo_data_path(), "**", "definition.yaml")
    langs = [_get_language_from_file(f) for f in glob(demo_glob)]
    langs.sort(key=lambda x: x.name)
    return langs


def load_demo_languages():
    """
    Load selected predefined languages.  Assume everything is supported.

    This method will also be called during acceptance tests, so it's public.
    """
    demo_langs = _demo_languages()
    langs = [
        lute.language.service.get_language_def(langname)["language"]
        for langname in demo_langs
    ]
    supported = [lang for lang in langs if lang.is_supported]
    for lang in supported:
        db.session.add(lang)
    db.session.commit()


def load_demo_stories():
    "Load the stories."
    demo_langs = _demo_languages()
    langdefs = [
        lute.language.service.get_language_def(langname) for langname in demo_langs
    ]
    langdefs = [d for d in langdefs if d["language"].is_supported]

    r = Repository(db)
    for d in langdefs:
        for b in d["books"]:
            r.add(b)
    r.commit()

    SystemSetting.set_value("IsDemoData", True)
    db.session.commit()
    refresh_stats()


def load_demo_data():
    """
    Load the data.
    """
    load_demo_languages()
    load_demo_stories()
    SystemSetting.set_value("IsDemoData", True)
    db.session.commit()
