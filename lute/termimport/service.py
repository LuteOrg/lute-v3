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


def import_file(filename, create_terms=True, update_terms=True, new_as_unknowns=False):
    """
    Validate and import file.

    Throws BadImportFileError if file contains invalid data.
    """
    import_data = _load_import_file(filename)
    _validate_data(import_data)
    return _do_import(import_data, create_terms, update_terms, new_as_unknowns)


def _load_import_file(filename, encoding="utf-8-sig"):
    "Create array of hashes from file."
    importdata = []
    with open(filename, "r", encoding=encoding) as f:
        reader = csv.DictReader(f)
        if reader.fieldnames:  # Avoid empty file error
            reader.fieldnames = [name.lower() for name in reader.fieldnames]

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

    allowed = required + [
        "translation",
        "parent",
        "status",
        "tags",
        "pronunciation",
        "link_status",
    ]
    ignored = ["added"]
    for k in field_list:
        if k not in allowed and k not in ignored:
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


def _import_term_skip_parents(repo, rec, lang, set_to_unknown=False):
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
    if set_to_unknown:
        t.status = 0
    if "pronunciation" in rec:
        t.romanization = rec["pronunciation"]
    if "tags" in rec:
        tags = list(map(str.strip, rec["tags"].split(",")))
        t.term_tags = [t for t in tags if t != ""]
    repo.add(t)


def _update_term_skip_parents(t, repo, rec):
    "Update a term in the repo."
    # Don't change the lang or text of the term
    # t.language = lang
    # t.language_id = lang.id
    # t.text = rec["term"]
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

    # If this is a status 0 ("unknown") term, and it's being updated,
    # then it's no longer unknown!
    if t.status == 0:
        t.status = 1

    repo.add(t)


def _set_term_parents(repo, rec, lang):
    "Set the term parents."
    t = repo.find(lang.id, rec["term"])
    parents = list(map(str.strip, rec["parent"].split(",")))
    t.parents = [p for p in parents if p != ""]
    if "link_status" in rec and len(parents) == 1:
        sync_status = rec["link_status"] or ""
        t.sync_status = sync_status.strip().lower() == "y"
    if len(t.parents) != 1:
        t.sync_status = False

    # If syncing to parent, and the term status was not explicitly set,
    # then "inherit" the parent status.
    if t.sync_status and len(t.parents) == 1 and "status" not in rec:
        p = repo.find(lang.id, t.parents[0])
        if p is not None:
            t.status = p.status

    repo.add(t)


def _do_import(
    import_data, create_terms=True, update_terms=True, new_as_unknowns=False
):
    """
    Import records.

    If create_terms is True, create new terms.
    If update_terms is True, update existing terms.
    If new_as_unknowns is True, new terms are given status 0.

    The import is done in two passes:
    1. import the basic terms, without setting their parents
    2. update the terms with parents

    The two passes are done because the import file may
    contain a parent in its own row, and we want that to be
    imported first to get its own specified data.
    """
    # pylint: disable=too-many-locals

    repo = Repository(db)

    skipped = 0

    # Keep track of the created and updated terms: we only want to
    # update these ones in pass #2.
    created_terms = []
    updated_terms = []

    def term_string(lang, term):
        return f"{lang.id}-{term}"

    for batch in [import_data[i : i + 100] for i in range(0, len(import_data), 100)]:
        langs_dict = _create_langs_dict(batch)
        for hsh in batch:
            lang = langs_dict[hsh["language"]]
            t = repo.find(lang.id, hsh["term"])
            ts = term_string(lang, hsh["term"])

            if create_terms and t is None:
                # Create a brand-new term.
                _import_term_skip_parents(repo, hsh, lang, new_as_unknowns)
                created_terms.append(ts)

            elif create_terms and t is not None and t.status == 0:
                # A status 0 "unknown" term can be created, but really
                # it's an update of an existing term.
                _update_term_skip_parents(t, repo, hsh)
                created_terms.append(ts)

            elif update_terms and t is not None and t.status != 0:
                # Can only update existing terms.
                _update_term_skip_parents(t, repo, hsh)
                updated_terms.append(ts)

            else:
                skipped += 1

        repo.commit()

    pass_2 = [t for t in import_data if "parent" in t and t["parent"] != ""]
    for batch in [pass_2[i : i + 100] for i in range(0, len(pass_2), 100)]:
        langs_dict = _create_langs_dict(batch)
        for hsh in batch:
            lang = langs_dict[hsh["language"]]
            ts = term_string(lang, hsh["term"])
            if ts in created_terms or ts in updated_terms:
                _set_term_parents(repo, hsh, lang)
        repo.commit()

    stats = {
        "created": len(created_terms),
        "updated": len(updated_terms),
        "skipped": skipped,
    }

    return stats
