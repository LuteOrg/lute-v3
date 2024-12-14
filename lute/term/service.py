"""
/term service for routes to use
"""

from lute.term.model import Repository


class Service:
    "Service."

    def __init__(self, session):
        self.session = session

    def bulk_set_parent(self, parenttext, termids):
        "Set parent for all terms, replace existing."
        parent = None
        repo = Repository(self.session)
        terms = [repo.load(tid) for tid in termids]
        lang_id = terms[0].language_id
        parent = repo.find(lang_id, parenttext)

        for term in terms:
            if term.parents != [parenttext]:
                term.parents = [parenttext]
                term.status = parent.status
                term.sync_status = True
            repo.add(term)
        repo.commit()
