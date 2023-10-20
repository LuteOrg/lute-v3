"""
Term business object and repository.

Terms are converted to and from lute.models.term.Term objects to save
them in the database.
"""

class Term:
    """
    Term business object.  All class members are primitives.
    """

    def __init__(self):
        self.id = None
        self.language_id = None
        self.original_text = None  # The original text given to the DTO, to track changes.
        self.text = None
        self.status = 1
        self.translation = None
        self.romanization = None
        self.term_tags = []
        self.flash_message = None
        self.parents = []
        self.current_image = None

class Repository:
    """
    Maps Term BO to and from lute.model.Term.
    """

    def __init__(self, db):
        self.db = db

    def add(self, Term):
        """
        Add a term to be saved to the db session.
        """

    def commit(self):
        """
        Commit everything.
        """
        self.db.session.commit()
