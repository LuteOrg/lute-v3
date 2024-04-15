"Language helper methods."


import os
import re
from glob import glob
import yaml

# from sqlalchemy import text

from lute.models.language import Language
from lute.book.model import Book, Repository

# from lute.book.stats import refresh_stats
from lute.db import db


def get_defs():
    "Return language definitions."
    ret = []
    def_glob = os.path.join(_language_defs_path(), "**", "definition.yaml")
    for f in glob(def_glob):
        entry = {}
        with open(f, "r", encoding="utf-8") as df:
            d = yaml.safe_load(df)
            entry["language"] = Language.from_dict(d)
        entry["books"] = _get_books(f)
        ret.append(entry)
    return ret


def _get_books(lang_definition_filename):
    "Get the stories in the same directory as the definition.yaml."
    books = []
    d, f = os.path.split(lang_definition_filename)
    story_glob = os.path.join(d, "*.txt")
    for filename in glob(story_glob):
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
        title_match = re.search(r"title:\s*(.*)\n", content)
        title = title_match.group(1).strip()
        content = re.sub(r"#.*\n", "", content)
        b = Book()
        b.title = title
        b.text = content
        books.append(b)
    return books


def load_language_def(lang_name):
    "Load a language def and its stories, save to database."
    defs = get_defs()
    load_def = [d for d in defs if d["language"].name == lang_name]
    if len(load_def) == 0:
        raise RuntimeError(f"Missing language def name {lang_name}")
    load_def = load_def[0]
    lang = load_def["language"]
    db.session.add(lang)
    db.session.commit()

    r = Repository(db)
    for b in load_def["books"]:
        b.language_id = lang.id
        r.add(b)
    r.commit()


def _language_defs_path():
    "Path to the definitions and stories."
    thisdir = os.path.dirname(__file__)
    d = os.path.join(thisdir, "..", "db", "language_defs")
    return os.path.abspath(d)
