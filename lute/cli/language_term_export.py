"""
Generate a rough data file for a given language for all terms.

Gets *all* books for a given language, and writes a data file to
the specified csv output file name.

Generates csv with headings:
term; count; familycount; books; definition; status; children

e.g.
term; count; familycount; books; definition; status; children
haber; 100; 1500; book1,book2; to exist; 99; hay (500), he (200), has (150) ...
"""

import csv
from lute.db import db
from lute.models.book import Book
from lute.read.render.service import get_paragraphs


def _add_term_to_dict(t, terms):
    "Add term to dictionary and return it."
    key = t.text_lc
    if key in terms:
        return terms[key]

    tag_list = ", ".join([tg.text for tg in t.term_tags])
    if tag_list == "":
        tag_list = "-"

    parents_text = sorted([p.text_lc for p in t.parents])
    parents_text = "; ".join(parents_text)
    if parents_text == "":
        parents_text = "-"

    zws = "\u200B"
    hsh = {
        "sourceterm": t,
        "term": t.text.replace(zws, ""),
        "count": 0,
        "familycount": 0,
        "books": [],
        "definition": t.translation or "-",
        "status": t.status,
        "parents": parents_text,
        "children": [],
        "tags": tag_list,
    }
    terms[key] = hsh
    return hsh


def _process_book(b, terms):
    "Process pages in book, add to output."
    print(f"Processing {b.title} ...")
    i = 0
    for text in b.texts:
        i += 1
        if i % 10 == 0:
            print(f"  page {i} of {b.page_count}", end="\r")
        paragraphs = get_paragraphs(text.text, b.language)
        displayed_terms = [
            ti.term
            for para in paragraphs
            for sentence in para
            for ti in sentence.textitems
            if ti.is_word and ti.term is not None
        ]
        for t in displayed_terms:
            e = _add_term_to_dict(t, terms)
            e["count"] += 1
            e["familycount"] += 1
            if b.title not in e["books"]:
                e["books"].append(b.title)

            for parent in t.parents:
                p = _add_term_to_dict(parent, terms)
                p["familycount"] += 1
                if b.title not in p["books"]:
                    p["books"].append(b.title)
                if t.text_lc not in p["children"]:
                    p["children"].append(t.text_lc)


def _book_list_truncated(title_array):
    "Return first 5 books, + count of rest."
    titles = list(set(title_array))
    first_5 = titles[:5]
    ret = ", ".join(first_5)
    count_rest = len(titles) - len(first_5)
    if count_rest > 0:
        ret += f" [... +{count_rest} more]"
    return ret


def _finalize_output(terms):
    "Convert terms hash to usable output."
    for _, hsh in terms.items():
        hsh["books"] = _book_list_truncated(hsh["books"])

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

    ret = terms.values()
    return sorted(ret, key=lambda x: (-x["familycount"], x["term"]))


def _generate_file(books, outfile_name):
    "Write data file for books to outfile_name."
    terms = {}
    for b in books:
        _process_book(b, terms)
    outdata = _finalize_output(terms)

    with open(outfile_name, "w", newline="", encoding="utf-8") as outfile:
        keys = [
            "term",
            "count",
            "familycount",
            "books",
            "definition",
            "status",
            "parents",
            "children",
            "tags",
        ]
        writer = csv.DictWriter(outfile, fieldnames=keys, extrasaction="ignore")
        writer.writeheader()
        for r in outdata:
            writer.writerow(r)


def generate_language_file(language_name, outfile_name):
    """
    Generate the datafile for the language.
    """
    books = db.session.query(Book).all()
    books = [b for b in books if b.language.name == language_name]
    if len(books) == 0:
        print(f"No books for given language {language_name}, quitting.")
    else:
        print(f"Writing to {outfile_name}")
        _generate_file(books, outfile_name)
        print("Done.                     ")  # extra space overwrites old output.


def generate_book_file(bookid, outfile_name):
    """
    Generate the datafile for the book.
    """
    books = db.session.query(Book).all()
    books = [b for b in books if f"{b.id}" == f"{bookid}"]
    if len(books) == 0:
        print(f"No book with id = {bookid}.")
    else:
        print(f"Writing to {outfile_name}")
        _generate_file(books, outfile_name)
        print("Done.                     ")  # extra space overwrites old output.
