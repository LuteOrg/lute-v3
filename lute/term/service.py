"""
/term service for routes to use
"""

from dataclasses import dataclass, field
from typing import List, Optional
from lute.models.term import Status
from lute.models.repositories import TermRepository, TermTagRepository
from lute.term.model import Repository


class TermServiceException(Exception):
    """
    Raised if something bad:

    - missing parent
    etc.
    """


# pylint: disable=too-many-instance-attributes
@dataclass
class BulkTermUpdateData:
    "Bulk updates"
    term_ids: List[int] = field(default_factory=list)
    lowercase_terms: bool = False
    remove_parents: bool = False
    parent_id: Optional[int] = None
    parent_text: Optional[str] = None
    change_status: bool = False
    status_value: Optional[int] = None
    add_tags: List[str] = field(default_factory=list)
    remove_tags: List[str] = field(default_factory=list)


class Service:
    "Service."

    def __init__(self, session):
        self.session = session

    def apply_bulk_updates(self, bulk_update_data):
        "Apply all updates."
        if len(bulk_update_data.term_ids) == 0:
            return

        parent = None
        repo = TermRepository(self.session)
        terms = [repo.find(tid) for tid in bulk_update_data.term_ids]

        lang_ids = list({term.language.id for term in terms})
        if len(lang_ids) > 1:
            raise TermServiceException("Terms not all the same language")

        # parent is found either by the ID, or if that returns None, by a text search.
        if bulk_update_data.parent_id is not None:
            parent = repo.find(bulk_update_data.parent_id)
        if parent is None and bulk_update_data.parent_text is not None:
            modelrepo = Repository(self.session)
            pmodel = modelrepo.find_or_new(lang_ids[0], bulk_update_data.parent_text)
            modelrepo.add(pmodel)
            modelrepo.commit()
            # Re-load it to get its id.  ... wasteful, not concerned at the moment.
            pmodel = modelrepo.find(lang_ids[0], bulk_update_data.parent_text)
            parent = repo.find(pmodel.id)

        ttrepo = TermTagRepository(self.session)
        add_tags = [ttrepo.find_or_create_by_text(a) for a in bulk_update_data.add_tags]
        remove_tags = [
            ttrepo.find_or_create_by_text(a) for a in bulk_update_data.remove_tags
        ]

        for term in terms:
            if bulk_update_data.lowercase_terms:
                term.text = term.text_lc
            if bulk_update_data.remove_parents:
                term.remove_all_parents()
                term.sync_status = False
            if parent is not None:
                term.remove_all_parents()
                term.add_parent(parent)
            if parent is not None and parent.status != Status.UNKNOWN:
                term.sync_status = True
                term.status = parent.status

            if (
                bulk_update_data.change_status is True
                and bulk_update_data.status_value is not None
            ):
                term.status = bulk_update_data.status_value

            for tag in add_tags:
                term.add_term_tag(tag)
            for tag in remove_tags:
                term.remove_term_tag(tag)

            self.session.add(term)
            self.session.commit()
