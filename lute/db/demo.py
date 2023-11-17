"""
Functions to manage demo database.

Lute db comes pre-loaded with some demo data.  User can view Tutorial,
wipe data, etc.

The db settings table contains a record, StKey = 'IsDemoData', if the
data is demo.
"""

import os
import re
from glob import glob
import yaml
from sqlalchemy import text

from lute.models.language import Language
from lute.models.book import Book
from lute.book.stats import refresh_stats
from lute.models.setting import SystemSetting
from lute.db import db
import lute.db.management


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


def demo_data_path():
    """
    Path to the demo data yaml files.
    """
    thisdir = os.path.dirname(__file__)
    demo_dir = os.path.join(thisdir, "demo")
    return os.path.abspath(demo_dir)


def get_demo_language(filename):
    """
    Create a new Language object from a yaml definition.
    """
    with open(filename, "r", encoding="utf-8") as file:
        d = yaml.safe_load(file)

    lang = Language()

    def load(key, method):
        if key in d:
            val = d[key]
            # Handle boolean values
            if isinstance(val, str):
                temp = val.lower()
                if temp == "true":
                    val = True
                elif temp == "false":
                    val = False
            setattr(lang, method, val)

    # Define mappings for fields
    mappings = {
        "name": "name",
        "dict_1": "dict_1_uri",
        "dict_2": "dict_2_uri",
        "sentence_translation": "sentence_translate_uri",
        "show_romanization": "show_romanization",
        "right_to_left": "right_to_left",
        "parser_type": "parser_type",
        "character_substitutions": "character_substitutions",
        "split_sentences": "regexp_split_sentences",
        "split_sentence_exceptions": "exceptions_split_sentences",
        "word_chars": "word_characters",
    }

    for key in d.keys():
        funcname = mappings.get(key, "")
        if funcname:
            load(key, funcname)

    return lang


def predefined_languages():
    "Languages that have yaml files."
    demo_glob = os.path.join(demo_data_path(), "languages", "*.yaml")
    langs = [get_demo_language(f) for f in glob(demo_glob)]
    langs.sort(key=lambda x: x.name)
    return langs


def load_demo_languages():
    """
    Load predefined languages.  Assume everything is supported.

    This method will also be called during acceptance tests, so it's "public".
    """
    supported = [lang for lang in predefined_languages() if lang.is_supported]
    for lang in supported:
        db.session.add(lang)
    db.session.commit()


def load_demo_stories():
    "Load the stories."
    demo_glob = os.path.join(demo_data_path(), "stories", "*.txt")
    for filename in glob(demo_glob):
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()

        langpatt = r"language:\s*(.*)\n"
        lang = re.search(langpatt, content).group(1).strip()
        lang = Language.find_by_name(lang)

        if lang is None or not lang.is_supported:
            pass
        else:
            title_match = re.search(r"title:\s*(.*)\n", content)
            title = title_match.group(1).strip()
            content = re.sub(r"#.*\n", "", content)
            b = Book.create_book(title, lang, content)
            db.session.add(b)
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
