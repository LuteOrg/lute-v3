"""
Term business object and repository.

Terms are converted to and from lute.models.term.Term objects to save
them in the database.
"""

from lute.db import db
from lute.models.term import Term as DBTerm, TermTag, TermFlashMessage, TermImage
from lute.models.language import Language


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


    def find_by_id(self, term_id):
        "Return a Term business object for the DBTerm with the id."
        t = DBTerm.find(term_id)
        if t is None:
            raise ValueError(f'No term with id {term_id} found')
        return self._build_business_term(t)


    def add(self, term):
        """
        Add a term to be saved to the db session.
        """
        dbterm = self._build_db_term(term)
        self.db.session.add(dbterm)


    def commit(self):
        """
        Commit everything.
        """
        self.db.session.commit()


    def _build_db_term(self, term):
        "Convert a term business object to a DBTerm."
        lang = Language.find(term.language_id)
        if lang is None:
            raise Exception(f'Unknown language {term.language_id} for term')
        if term.text is None:
            raise Exception('Text not set for term')

        t = self._find_by_langid_and_text(lang.id, term.text)
        if t is None:
            t = DBTerm()

        t.language = lang
        t.text = term.text
        t.status = term.status
        t.translation = term.translation
        t.romanization = term.romanization
        t.current_image = term.current_image

        termtags = []
        for s in term.term_tags:
            termtags.append(TermTag.find_or_create_by_text(s))
        t.remove_all_term_tags()
        for tt in termtags:
            t.add_term_tag(tt)

        termparents = []
        create_parents = [
            p for p in term.parents
            if p is not None and p != '' and
            lang.get_lowercase(term.text) != lang.get_lowercase(p)]
        for p in create_parents:
            termparents.append(self._find_or_create_parent(p, term, termtags))
        t.remove_all_parents()
        for tp in termparents:
            t.add_parent(tp)

        return t


    def _find_by_langid_and_text(self, langid, text):
        lang = Language.find(langid)
        text_lc = lang.get_lowercase(text)
        query = db.session.query(DBTerm).filter(
            DBTerm.language_id == langid,
            DBTerm.text_lc == text_lc
        )
        terms = query.all()
        if not terms:
            return None
        return terms[0]


    def _find_or_create_parent(self, pt, language, term, termtags) -> Term:
        p = term_service.find(pt, term.language)

        if p is not None:
            if (p.translation or '') == '':
                p.translation = term.translation
            if (p.current_image or '') == '':
                p.current_image = term.current_image
            return p

        p = DBTerm(language, pt)
        p.status = term.status
        p.translation = term.translation
        p.current_image = term.current_image
        for tt in termtags:
            p.add_term_tag(tt)

        return p


    def _build_business_term(self, dbterm):
        "Create a Term bus. object from a lute.model.term.Term."
        term = Term()
        term.id = dbterm.id
        term.language_id = dbterm.language.id

        # Remove zero-width spaces (zws) from strings for user forms.
        text = dbterm.text
        zws = '\u200B'  # zero-width space
        text = text.replace(zws, '')
        term.original_text = text
        term.text = text

        term.status = dbterm.status
        term.translation = dbterm.translation
        term.romanization = dbterm.romanization
        term.token_count = dbterm.token_count
        term.current_image = dbterm.get_current_image()
        term.flash_message = dbterm.get_flash_message()
        term.term_parents = [p.text for p in dbterm.parents]
        term.romanization = dbterm.romanization
        term.term_tags = [tt.text for tt in dbterm.term_tags]

        return term
