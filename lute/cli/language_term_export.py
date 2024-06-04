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
from collections import Counter
from lute.db import db
from lute.models.book import Book
from lute.term.model import Repository
from lute.read.render.service import get_paragraphs


def get_dist(book, collector, termrepo, language_id):  # pylint: disable=too-many-locals
    """
    Get word distribution in book.

    The data is added to the collector dictionary.
    """

    # Get all terms and counts.
    fulltext = "\n".join([t.text for t in book.texts])
    pts = book.language.get_parsed_tokens(fulltext)
    words = [pt.token for pt in pts if pt.is_word]

    # distrib = { 'term1': count1, 'term2': count2, ... }
    distrib = dict(Counter(words))

    # The distribution doesn't handle capitalization, so it will
    # contain things like { 'There': 10, 'there': 20 }.  Do a lookup
    # for each term ('There', 'there') in the repository to see if a
    # matching term with a standardized term.text is found.
    normalized = {}

    totcount = len(distrib.keys())
    i = 0
    print(f"Loading data for book {book.title} ...")
    for k, v in distrib.items():
        i += 1
        if i % 100 == 0:
            print(f"  {i} of {totcount}", end="\r")
        norm_word = termrepo.find_or_new(language_id, k)
        norm_entry = normalized.get(norm_word.text, {"count": 0, "parents": []})
        norm_entry["count"] += v
        norm_entry["parents"] = norm_word.parents
        normalized[norm_word.text] = norm_entry

    # normalized = { 'there': { 'count': 30, 'parents': [...] }, ... }.
    #
    # The collector may already have the term ('there') from prior
    # books, so combine those.
    for t, n in normalized.items():  # pylint: disable=redefined-outer-name
        entry = collector.get(t, {"term": t, "count": 0, "books": []})
        entry["count"] += n["count"]
        entry["books"].append(book.title)
        collector[t] = entry

        # The term may have a parent that isn't actually present in any book!
        # We need to add those parents to the collector as well, or later
        # searches for the parent will fail.
        for p in n["parents"]:
            pentry = collector.get(p, {"term": p, "count": 0, "books": []})
            collector[p] = pentry


def _load_hash_from_term(t, term):
    "Load common data to hash."
    t["parent"] = ", ".join(term.parents)
    t["definition"] = term.translation or "-"
    t["status"] = term.status if term.id is not None else "-"
    t["children"] = "-"
    t["childbooks"] = []
    t["tags"] = ", ".join(term.term_tags)


def load_term_data(langid, terms, repo):
    "Load basic data."
    totcount = len(terms.keys())
    i = 0
    print("Loading term data ...")
    for k, t in terms.items():  # pylint: disable=unused-variable
        i += 1
        if i % 100 == 0:
            print(f"  {i} of {totcount}", end="\r")

        term = repo.find_or_new(langid, t["term"])
        _load_hash_from_term(t, term)
        t["familycount"] = t["count"]


def load_parent_data(langid, terms, repo):
    "Get and print data."

    parents = list({t["parent"] for t in terms.values() if t["parent"] != ""})

    missingparents = [p for p in parents if p not in terms]
    totcount = len(missingparents)
    i = 0
    print("Loading missing parents ...")
    for p in missingparents:
        i += 1
        if i % 100 == 0:
            print(f"  {i} of {totcount}", end="\r")

        term = repo.find_or_new(langid, p)
        t = {"term": p, "count": 0, "books": []}
        _load_hash_from_term(t, term)
        t["familycount"] = 0
        terms[p] = t

    totcount = len(parents)
    i = 0
    print("Finalizing parent data ...")
    for p in parents:
        i += 1
        if i % 100 == 0:
            print(f"  {i} of {totcount}", end="\r")

        children = [c for c in terms.values() if c["parent"] == p]
        csorted = sorted(children, key=lambda c: c["count"], reverse=True)
        children_string = "; ".join([f"{c['term']} ({c['count']})" for c in csorted])
        childbooks = [c["books"] for c in children]
        childbooks = list({b for blist in childbooks for b in blist})
        childtotcount = sum(c["count"] for c in children)

        terms[p]["children"] = children_string
        terms[p]["childbooks"] = childbooks
        terms[p]["familycount"] += childtotcount


def get_output_data(terms):
    "Get the final set of output data."
    printterms = [
        t for t in terms.values() if t["parent"] == "" or t["children"] != "-"
    ]

    # Clean up data for printing.
    for t in printterms:
        t["books"] = list(set(t["books"] + t["childbooks"]))
        t["books"] = "; ".join(t["books"])
        del t["childbooks"]

    return printterms


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
    langid = lang.id

    repo = Repository(db)
    terms = {}

    def _add_term_if_needed(t):
        if t.text_lc in terms:
            return
        tag_list = ", ".join([tg.text for tg in t.term_tags])
        if tag_list == "":
            tag_list = "-"

        zws = "\u200B"
        terms[t.text_lc] = {
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
                _add_term_if_needed(t)
                e = terms[t.text_lc]
                e["count"] += 1
                e["familycount"] += 1
                if b.title not in e["books"]:
                    e["books"].append(b.title)

                for parent in t.parents:
                    _add_term_if_needed(parent)
                    p = terms[parent.text_lc]
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
