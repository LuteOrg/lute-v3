"""
Export language definition and first two pages of all books to lute/db/language_defs/

Run this as a module from the root directory, with languages to export as args:

python -m scripts.dump_lang_data Catalan Bulgarian

NOTE: this script assumes that the config is in the root folder, or at lute/config/config.yml.
"""

import sys
import os
import yaml

from lute.models.book import Book
from lute.models.language import Language
from lute.db import db
import lute.app_factory


def _language_defs_path():
    "Path to the definitions and stories."
    thisdir = os.path.dirname(__file__)
    d = os.path.join(thisdir, "..", "lute", "db", "language_defs")
    return os.path.abspath(d)


def _partial_book_content(b):
    "Get book content as string."
    fulltext = [t.text for t in b.texts]
    first_two_pages = fulltext[:2]
    s = "\n".join(first_two_pages).replace("\r", "").strip()
    return f"# title: {b.title}\n\n{s}"


def _write_langs(language_names, outdir):
    "Write all langs and books."
    langs = db.session.query(Language).all()
    langs = [lang for lang in langs if lang.name.lower() in language_names]
    for lang in langs:
        ld = lang.to_dict()
        n = ld["name"].lower().replace(" ", "_")
        langdir = os.path.join(outdir, n)
        if not os.path.exists(langdir):
            os.mkdir(langdir)

        file_path = os.path.join(langdir, "definition.yaml")
        with open(file_path, "w", encoding="utf-8") as fp:
            yaml.dump(ld, stream=fp, allow_unicode=True, sort_keys=False)
        print(lang.name)

        books = db.session.query(Book).filter(Book.language == lang).all()
        books = [b for b in books if not b.archived]
        story_count = 1
        for b in books:
            filename = f"story_{story_count}"
            story_count += 1
            file_path = os.path.join(langdir, f"{filename}.txt")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(_partial_book_content(b))
            file_size_kb = os.path.getsize(file_path) / 1024
            print(f"- {filename} ({file_size_kb:.2f} KB)")


def main(langnames):
    "Entry point."
    outputdir = _language_defs_path()
    print(f"Outputting to {outputdir}")

    langnames = [n.lower() for n in langnames]
    langnames = list(set(langnames))
    app = lute.app_factory.create_app()
    with app.app_context():
        _write_langs(langnames, outputdir)


#####################
# Entry point.

if len(sys.argv) < 2:
    print("Language names required.")
    sys.exit(0)

main(sys.argv[1:])
