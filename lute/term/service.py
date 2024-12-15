"""
/term service for routes to use
"""

from lute.term.model import Repository


class TermServiceException(Exception):
    """
    Raised if something bad:

    - missing parent
    etc.
    """


class Service:
    "Service."

    def __init__(self, session):
        self.session = session

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

        lang_id = lang_ids[0]
        parent = repo.find(lang_id, parenttext)

        if parent is None:
            msg = f"Parent {parenttext} not found."
            raise TermServiceException(msg)

        for term in terms:
            if term.parents != [parenttext]:
                term.parents = [parenttext]
                term.status = parent.status
                term.sync_status = True
            repo.add(term)
        repo.commit()
