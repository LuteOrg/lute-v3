"""
Term import.
"""

import csv

from lute.db import db
from lute.models.term import Status
from lute.models.language import Language
from lute.term.model import Term, Repository


class BadImportFileError(Exception):
    """
    Raised if the import file is bad:

    - unknown language or status
    - dup term
    etc.
    """


def import_file(filename):
    """
    Validate and import file.

    Throws BadImportFileError if file contains invalid data.
    """
    import_data = _load_import_file(filename)
    _validate_data(import_data)
    return _do_import(import_data)


def _load_import_file(filename, encoding="utf-8-sig"):
    "Create array of hashes from file."
    importdata = []
    with open(filename, "r", encoding=encoding) as f:
        reader = csv.DictReader(f)

        fieldnames = reader.fieldnames
        if fieldnames is None:
            raise BadImportFileError("No terms in file")
        _validate_data_fields(fieldnames)

        for line in reader:
            importdata.append(line)

    if len(importdata) == 0:
        raise BadImportFileError("No terms in file")

    return importdata


def _validate_data_fields(field_list):
    "Check the keys in the file."
    required = ["language", "term"]
    for k in required:
        if k not in field_list:
            raise BadImportFileError(f"Missing required field '{k}'")

    allowed = required + ["translation", "parent", "status", "tags", "pronunciation"]
    for k in field_list:
        if k not in allowed:
            raise BadImportFileError(f"Unknown field '{k}'")


def _validate_data(import_data):
    """
    Check the data.
    """
    _validate_languages(import_data)
    _validate_terms_exist(import_data)
    _validate_statuses(import_data)
    _validate_no_duplicate_terms(import_data)


def _create_langs_dict(import_data):
    "Create dictionary of language name to Language."
    lang_dict = {}
    langs = [hsh["language"].strip() for hsh in import_data]
    for lang_name in list(set(langs)):
        lang_dict[lang_name] = Language.find_by_name(lang_name)
    return lang_dict


def _get_status(s):
    "Convert status to db value."
    status_map = {
        "": 1,
        "1": 1,
        "2": 2,
        "3": 3,
        "4": 4,
        "5": 5,
        "W": Status.WELLKNOWN,
        "I": Status.IGNORED,
    }
    return status_map.get(s)


def _validate_languages(import_data):
    "Validate the languages."
    lang_dict = _create_langs_dict(import_data)
    for lang_name, lang in lang_dict.items():
        if lang is None:
            raise BadImportFileError(f"Unknown language '{lang_name}'")


def _validate_statuses(import_data):
    "All statuses must be valid."
    statuses = [hsh["status"].strip() for hsh in import_data if "status" in hsh]
    for s in set(statuses):
        if _get_status(s) is None:
            raise BadImportFileError(
                "Status must be one of 1, 2, 3, 4, 5, I, W, or blank"
            )


def _validate_terms_exist(import_data):
    "All records must have a term."
    blanks = [hsh for hsh in import_data if hsh["term"].strip() == ""]
    if len(blanks) > 0:
        raise BadImportFileError("Term is required")


def _validate_no_duplicate_terms(import_data):
    """
    Duplicate terms aren't allowed.

    If file contained two duplicate terms, which is the "correct" one?
    """

    def make_lang_term_string(hsh):
        t = hsh["term"].strip()
        # Have to also clear unicode whitespace.
        t = " ".join(t.split())
        return f"{hsh['language']}: {t.lower()}"

    lang_terms = [make_lang_term_string(hsh) for hsh in import_data]
    term_counts = {}
    for term in lang_terms:
        term_counts[term] = term_counts.get(term, 0) + 1
    duplicates = [term for term, count in term_counts.items() if count > 1]
    if len(duplicates) != 0:
        raise BadImportFileError(f"Duplicate terms in import: {', '.join(duplicates)}")


def _import_term_skip_parents(repo, rec, lang):
    "Add a single record to the repo."
    t = Term()
    t.language = lang
    t.language_id = lang.id
    t.text = rec["term"]
    if "translation" in rec:
        t.translation = rec["translation"]
    if "status" in rec:
        status = _get_status(rec["status"])
        if status is not None:
            t.status = int(status)
    if "pronunciation" in rec:
        t.romanization = rec["pronunciation"]
    if "tags" in rec:
        tags = list(map(str.strip, rec["tags"].split(",")))
        t.term_tags = [t for t in tags if t != ""]
    repo.add(t)


def _set_term_parents(repo, rec, lang):
    "Set the term parents."
    t = repo.find(lang.id, rec["term"])
    parents = list(map(str.strip, rec["parent"].split(",")))
    t.parents = [p for p in parents if p != ""]
    repo.add(t)


def _do_import(import_data):
    """
    Import records.

    The import is done in two passes:
    1. import the basic terms, without setting their parents
    2. update the terms with parents

    The two passes are done because the import file may
    contain a parent in its own row, and we want that to be
    imported first to get its own specified data.
    """
    repo = Repository(db)

    skipped = 0

    # Keep track of the created terms: we only want to update
    # these ones in pass #2.
    created_terms = []

    def term_string(lang, term):
        return f"{lang.id}-{term}"

    for batch in [import_data[i : i + 100] for i in range(0, len(import_data), 100)]:
        langs_dict = _create_langs_dict(batch)
        for hsh in batch:
            lang = langs_dict[hsh["language"]]
            if repo.find(lang.id, hsh["term"]) is None:
                _import_term_skip_parents(repo, hsh, lang)
                created_terms.append(term_string(lang, hsh["term"]))
            else:
                skipped += 1
        repo.commit()

    pass_2 = [t for t in import_data if "parent" in t and t["parent"] != ""]
    for batch in [pass_2[i : i + 100] for i in range(0, len(pass_2), 100)]:
        langs_dict = _create_langs_dict(batch)
        for hsh in batch:
            lang_name = hsh["language"]
            lang = langs_dict[lang_name]
            if term_string(lang, hsh["term"]) in created_terms:
                _set_term_parents(repo, hsh, lang)
        repo.commit()

    stats = {"created": len(created_terms), "skipped": skipped}

    return stats
