"""
Term parent mapping.
"""

import csv
from sqlalchemy import text
from lute.db import db
from lute.models.term import Term, Status
from lute.term.model import Repository


## Exports


def export_terms_without_parents(language, outfile):
    "Export terms without parents in the language to filename outfile."
    # All existing terms that don't have parents.
    sig = Status.IGNORED
    sql = f"""
        SELECT w.WoTextLC
        FROM words w
        LEFT JOIN wordparents ON WpWoID = w.WoID
        WHERE w.WoLgID = {language.id}
          AND WpWoID IS NULL
          AND w.WoTokenCount = 1
          AND w.WoStatus != {sig}
    """
    data = db.session.execute(text(sql)).fetchall()
    terms = [term[0] for term in data]
    with open(outfile, "w", encoding="utf-8") as f:
        f.write("\n".join(terms))


def export_unknown_terms(book, outfile):
    "Export unknown terms in the book to outfile."
    lang = book.language
    unique_tokens = {
        t for txt in book.texts for t in lang.get_parsed_tokens(txt.text) if t.is_word
    }
    unique_lcase_toks = {lang.get_lowercase(t.token) for t in unique_tokens}

    lgid = lang.id
    known_terms_lc = (
        db.session.query(Term.text_lc)
        .filter(Term.language_id == lgid, Term.token_count == 1)
        .all()
    )
    known_terms_lc = [word[0] for word in known_terms_lc]

    newtoks = [t for t in unique_lcase_toks if t not in known_terms_lc]
    with open(outfile, "w", encoding="utf-8") as f:
        f.write("\n".join(newtoks))


## Imports


class BadImportFileError(Exception):
    """
    Raised if the import file is bad.
    """


def import_file(language, filename):
    """
    Validate and import file.

    Throws BadImportFileError if file contains invalid data.
    """
    import_data = _load_import_file(filename)
    _validate_data(import_data)
    return _do_import(language, import_data)


def _load_import_file(filename, encoding="utf-8-sig"):
    "Create array of hashes from file."
    importdata = []
    with open(filename, "r", encoding=encoding) as f:
        reader = csv.DictReader(f)

        fieldnames = reader.fieldnames
        if fieldnames is None:
            raise BadImportFileError("No mappings in file")
        _validate_data_fields(fieldnames)

        for line in reader:
            importdata.append(line)

    if len(importdata) == 0:
        raise BadImportFileError("No mappings in file")

    return importdata


def _validate_data_fields(field_list):
    "Check the keys in the file."
    for k in ["parent", "term"]:
        if k not in field_list:
            msg = "File must contain headings 'parent' and 'term'"
            raise BadImportFileError(msg)


def _validate_data(import_data):
    "All records must have parent, term."
    blanks = [
        hsh
        for hsh in import_data
        if hsh["term"].strip() == "" or hsh["parent"].strip() == ""
    ]
    if len(blanks) > 0:
        raise BadImportFileError("Term is required")


class ImportRecord:
    "Record in the import file."

    repo = None
    language = None

    @classmethod
    def set_context(cls, repo, language):
        "ImportRecord needs context for lookups."
        cls.repo = repo
        cls.language = language

    def _find(self, t):
        return ImportRecord.repo.find(ImportRecord.language.id, t)

    def __init__(self, hsh):
        self.ptext = hsh["parent"]
        self.parent = self._find(self.ptext)
        self.ctext = hsh["term"]
        self.child = self._find(self.ctext)

    @staticmethod
    def records(import_data):
        """
        Convert import data to records.

        This is called periodically during the import
        as each step updates the database.
        """
        return [ImportRecord(hsh) for hsh in import_data]


def _do_import(language, import_data):
    """
    Import records.
    """
    repo = Repository(db)
    ImportRecord.set_context(repo, language)

    updated = 0
    created = 0

    created, updated = _import_child_exists_parent_no(
        import_data, language, repo, created, updated
    )
    created, updated = _import_parent_exists_child_no(
        import_data, language, repo, created, updated
    )
    created, updated = _import_add_extra_parent_child_links(
        import_data, repo, created, updated
    )

    stats = {"created": created, "updated": updated}

    return stats


def _import_child_exists_parent_no(import_data, language, repo, created, updated):
    "Add parent and relationship."
    records = [
        p
        for p in ImportRecord.records(import_data)
        if p.parent is None and p.child is not None
    ]

    def _get_flash_msg(ptext):
        "Build a flash message for a new parent."
        all_children = [d.ctext for d in records if d.ptext == ptext]
        msg = f'Auto-created parent for "{all_children[0]}"'
        remaining = len(all_children) - 1
        if remaining > 0:
            msg += f" + {remaining} more"
        return msg

    # First add all the unique parents.
    ptexts = list({p.ptext for p in records})
    for p in ptexts:
        parent = repo.find_or_new(language.id, p)
        parent.flash_message = _get_flash_msg(p)
        repo.add(parent)
        created += 1
    repo.commit()

    # Then add all the relationships.
    for p in records:
        p.child.parents.append(p.ptext)
        repo.add(p.child)
        updated += 1
    repo.commit()

    return created, updated


def _import_parent_exists_child_no(import_data, language, repo, created, updated):
    "Add child and relationship."
    records = [
        p
        for p in ImportRecord.records(import_data)
        if p.parent is not None and p.child is None
    ]
    # Add all the children and relationships.
    for p in records:
        child = repo.find_or_new(language.id, p.ctext)
        if child.id is None:
            created += 1
        flash_msg = f'Auto-created and mapped to parent "{p.ptext}"'
        child.flash_message = flash_msg
        child.parents.append(p.ptext)
        repo.add(child)
    repo.commit()

    return created, updated


def _import_add_extra_parent_child_links(import_data, repo, created, updated):
    "Add parent to child if needed."
    records = [
        p
        for p in ImportRecord.records(import_data)
        if p.parent is not None
        and p.child is not None
        and p.parent.id != p.child.id
        and p.parent.text not in p.child.parents
    ]
    for p in records:
        p.child.parents.append(p.parent.text)
        repo.add(p.child)
        updated += 1
    repo.commit()

    return created, updated
