"""
Generate a rough data file for a given language for all terms.

Gets *all* books for a given language, and writes a data file to
the specified csv output file name.

Generates csv with headings:
term; count; familycount; books; definition; status; children

e.g.
term; count; familycount; books; definition; status; children
haber; 100; 1500; book1,book2; to exist; 99; hay (500), he (200), has (150) ...

There is probably a far better way to do this, likely using something
fairly heavyweight like pandas.  This works well enough for now.
"""

import sys
import csv
from lute.db import db
from lute.models.book import Book
from lute.read.render.service import get_paragraphs


def generate_file(language_name, outfile_name):
    """
    Generate the datafile for the language.
    """
    # pylint: disable=too-many-locals

    books = db.session.query(Book).all()
    books = [b for b in books if b.language.name == language_name]
    if len(books) == 0:
        print(f"No books for given language {language_name}, quitting.")
        sys.exit(0)

    lang = books[0].language
    terms = {}

    def _add_term_to_dict(t):
        key = t.text_lc
        if key in terms:
            return terms[key]

        tag_list = ", ".join([tg.text for tg in t.term_tags])
        if tag_list == "":
            tag_list = "-"

        zws = "\u200B"
        hsh = {
            "sourceterm": t,
            "term": t.text.replace(zws, ""),
            "count": 0,
            "familycount": 0,
            "books": [],
            "definition": t.translation or "-",
            "status": t.status,
            "children": [],
            "tags": tag_list,
        }
        terms[key] = hsh
        return hsh

    for b in books:
        print(f"Loading data for book {b.title} ...")
        i = 0
        for text in b.texts:
            i += 1
            if i % 10 == 0:
                print(f"  page {i} of {b.page_count()}", end="\r")
            paragraphs = get_paragraphs(text.text, lang)
            displayed_terms = [
                ti.term
                for para in paragraphs
                for sentence in para
                for ti in sentence.textitems
                if ti.is_word and ti.term is not None
            ]
            for t in displayed_terms:
                e = _add_term_to_dict(t)
                e["count"] += 1
                e["familycount"] += 1
                if b.title not in e["books"]:
                    e["books"].append(b.title)

                for parent in t.parents:
                    p = _add_term_to_dict(parent)
                    p["familycount"] += 1
                    if b.title not in p["books"]:
                        p["books"].append(b.title)
                    if t.text_lc not in p["children"]:
                        p["children"].append(t.text_lc)

    for _, hsh in terms.items():
        hsh["books"] = ", ".join(list(set(hsh["books"])))
        # children to child (count)
        children = []
        for key in hsh["children"]:
            t = terms[key]
            children.append({"count": t["count"], "term": t["sourceterm"].text})
        csorted = sorted(children, key=lambda c: c["count"], reverse=True)
        children_string = "; ".join([f"{c['term']} ({c['count']})" for c in csorted])
        if children_string == "":
            children_string = "-"
        hsh["children"] = children_string

    outdata = terms.values()

    ptsorted = sorted(outdata, key=lambda x: (-x["familycount"], x["term"]))
    keys = [
        "term",
        "count",
        "familycount",
        "books",
        "definition",
        "status",
        "children",
        "tags",
    ]
    print(f"Writing to {outfile_name}")
    with open(outfile_name, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=keys, extrasaction="ignore")
        writer.writeheader()
        for r in ptsorted:
            writer.writerow(r)
    print("Done.")
