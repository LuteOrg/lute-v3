"""
/term service for routes to use
"""

from dataclasses import dataclass, field
from lute.term.model import Repository


class TermServiceException(Exception):
    """
    Raised if something bad:

    - missing parent
    etc.
    """


@dataclass
class BulkTermUpdateData:
    "Bulk updates"
    term_ids: list[int] = field(default_factory=list)
    remove_parents: bool = False
    parent_id: int = None
    parent_text: str = None
    change_status: bool = False
    status_value: int = None
    add_tags: list[str] = field(default_factory=list)
    remove_tags: list[str] = field(default_factory=list)


class Service:
    "Service."

    def __init__(self, session):
        self.session = session

    def apply_bulk_updates(self, bulk_update_data):
        "Apply all updates."

    def bulk_set_parent(self, parenttext, termids):
        "Set parent for all terms, replace existing."
        if len(termids) == 0:
            return

        parent = None
        repo = Repository(self.session)
        terms = [repo.load(tid) for tid in termids]

        lang_ids = list({term.language_id for term in terms})
        if len(lang_ids) > 1:
            raise TermServiceException("Terms not all the same language")

        parent_list = []
        if parenttext.strip() != "":
            lang_id = lang_ids[0]
            parent = repo.find(lang_id, parenttext)
            if parent is None:
                msg = f"Parent {parenttext} not found."
                raise TermServiceException(msg)
            parent_list = [parenttext]

        for term in terms:
            if term.parents != parent_list:
                term.parents = parent_list
                term.sync_status = True
            if parent is not None:
                term.status = parent.status
            repo.add(term)
        repo.commit()

    def bulk_add_tags(self, tagtexts, termids):
        "Add tag for all terms."
        if len(termids) == 0:
            return

        repo = Repository(self.session)
        terms = [repo.load(tid) for tid in termids]
        for term in terms:
            term.term_tags.extend(tagtexts)
            repo.add(term)
        repo.commit()

    def bulk_remove_tags(self, tagtexts, termids):
        "Remove tag for all terms."
        if len(termids) == 0:
            return

        repo = Repository(self.session)
        terms = [repo.load(tid) for tid in termids]
        for term in terms:
            term.term_tags = [t for t in term.term_tags if t not in tagtexts]
            repo.add(term)
        repo.commit()
