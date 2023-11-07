"""
Term business object and repository.

Terms are converted to and from lute.models.term.Term objects to save
them in the database.
"""

import re
import functools
from sqlalchemy import and_, text as sqlalchtext

from lute.models.term import Term as DBTerm, TermTag
from lute.models.language import Language


class Term:  # pylint: disable=too-many-instance-attributes
    """
    Term business object.  All class members are primitives.
    """

    def __init__(self):
        # The ID of the DBTerm.
        self.id = None
        # A language object is required as the Term bus. object
        # must downcase the text and the original_text to see
        # if anything has changed.
        self._language = None
        # Ideally this wouldn't be needed, but the term form
        # populates this field with the (primitive) language id.
        self.language_id = None
        # The text.
        self.text = None
        self.text_lc = None
        # The original text given to the DTO, to track changes.
        self.original_text = None
        self.status = 1
        self.translation = None
        self.romanization = None
        self.term_tags = []
        self.flash_message = None
        self.parents = []
        self.current_image = None

    def __repr__(self):
        return (
            f'<Term BO "{self.text}" lang_id={self.language_id} lang={self.language}>'
        )

    @property
    def language(self):
        "Use or get the language."
        if self._language is not None:
            return self._language
        return Language.find(self.language_id)

    @language.setter
    def language(self, lang):
        if not isinstance(lang, Language):
            raise ValueError("not a language")
        self._language = lang

    def text_has_changed(self):
        "Check the downcased original text with the current text."
        # print(f'checking if changed, orig = "{self.original_text}", text = "{self.text}"')
        if self.original_text in ("", None):
            return False

        def get_lc(s):
            return self.language.get_lowercase(s)

        return get_lc(self.original_text) != get_lc(self.text)


class TermReference:
    "Where a Term has been used in books."

    def __init__(
        self, bookid, txid, pgnum, title, sentence=None
    ):  # pylint: disable=too-many-arguments
        self.book_id = bookid
        self.text_id = txid
        self.page_number = pgnum
        self.title = title
        self.sentence = sentence


class Repository:
    """
    Maps Term BO to and from lute.model.Term.
    """

    def __init__(self, _db):
        self.db = _db

        # Identity map for business lookup.
        # Note that the same term is stored
        # a few times: by upper case or lower case text,
        # plus language ID.
        self.identity_map = {}

    def _id_map_key(self, langid, text):
        return f"key-{langid}-{text}"

    def _add_to_identity_map(self, t):
        "Add found term to identity map."
        for txt in t.text, t.text_lc:
            k = self._id_map_key(t.language_id, txt)
            self.identity_map[k] = t

    def _search_identity_map(self, langid, txt):
        "Search the map w/ the given bus. key."
        k = self._id_map_key(langid, txt)
        if k in self.identity_map:
            return self.identity_map[k]
        return None

    def load(self, term_id):
        "Loads a Term business object for the DBTerm with the id."
        dbt = DBTerm.find(term_id)
        if dbt is None:
            raise ValueError(f"No term with id {term_id} found")
        term = self._build_business_term(dbt)
        self._add_to_identity_map(term)
        return term

    def find(self, langid, text):
        """
        Return a Term business object for the DBTerm with the langid and text.
        If no match, return None.
        """
        term = self._search_identity_map(langid, text)
        if term is not None:
            return term

        spec = self._search_spec_term(langid, text)
        dbt = DBTerm.find_by_spec(spec)
        if dbt is None:
            return None
        term = self._build_business_term(dbt)
        self._add_to_identity_map(term)
        return term

    def find_or_new(self, langid, text):
        """
        Return a Term business object for the DBTerm with the langid and text.
        If no match, return a new term with the text and language.

        If it's new, don't add to the identity map ... it's not saved yet,
        and so if we search for it again we should hit the db again.
        """
        t = self.find(langid, text)
        if t is not None:
            return t

        spec = self._search_spec_term(langid, text)
        t = Term()
        t.language = spec.language
        t.language_id = langid
        t.text = text
        t.text_lc = spec.text_lc
        t.original_text = text

        return t

    def find_matches(self, langid, text, max_results=50):
        """
        Return array of Term business objects for the DBTerms
        with the same langid, matching the text.
        If no match, return [].
        """
        spec = self._search_spec_term(langid, text)
        text_lc = spec.text_lc
        search = text_lc.strip() if text_lc else ""
        if search == "":
            return []

        matches = (
            self.db.session.query(DBTerm)
            .filter(
                and_(DBTerm.language_id == langid, DBTerm.text_lc.like(search + "%"))
            )
            .all()
        )

        exact = [t for t in matches if t.text_lc == text_lc]

        def compare(item1, item2):
            c1 = len(item1.children)
            c2 = len(item2.children)
            if c1 > c2:
                return -1
            if c1 < c2:
                return 1
            t1 = item1.text_lc
            t2 = item2.text_lc
            if t1 < t2:
                return -1
            if t1 > t2:
                return 1
            return 0

        remaining = [t for t in matches if t.text_lc != text_lc]
        # for t in remaining:
        #     print(f'term: {t.text}; child count = {len(t.children)}')
        remaining.sort(key=functools.cmp_to_key(compare))
        # print('remaining = ')
        # print(remaining)
        ret = exact + remaining
        ret = ret[:max_results]
        return [self._build_business_term(t) for t in ret]

    def get_term_tags(self):
        "Get all available term tags, helper method."
        tags = self.db.session.query(TermTag).all()
        return [t.text for t in tags]

    def add(self, term):
        """
        Add a term to be saved to the db session.
        Returns DB Term for tests and verification only,
        clients should not change it.
        """
        dbterm = self._build_db_term(term)
        self.db.session.add(dbterm)
        return dbterm

    def delete(self, term):
        """
        Add term to be deleted to session.
        """
        spec = self._search_spec_term(term.language_id, term.text)
        dbt = DBTerm.find_by_spec(spec)
        if dbt is None:
            return
        self.db.session.delete(dbt)

    def commit(self):
        """
        Commit everything.
        """
        self.db.session.commit()

    def _search_spec_term(self, langid, text):
        """
        Make a term to get the correct text_lc to search for.

        Creating a term does parsing and correct downcasing,
        so term.language.id and term.text_lc match what the
        db would contain.
        """
        lang = Language.find(langid)
        return DBTerm(lang, text)

    def _build_db_term(self, term):
        "Convert a term business object to a DBTerm."
        if term.text is None:
            raise ValueError("Text not set for term")

        spec = self._search_spec_term(term.language_id, term.text)
        t = DBTerm.find_by_spec(spec)
        if t is None:
            t = DBTerm()

        t.language = spec.language
        t.text = term.text
        t.original_text = term.text
        t.status = term.status
        t.translation = term.translation
        t.romanization = term.romanization
        t.set_current_image(term.current_image)

        if term.flash_message is not None:
            t.set_flash_message(term.flash_message)
        else:
            t.pop_flash_message()

        termtags = []
        for s in term.term_tags:
            termtags.append(TermTag.find_or_create_by_text(s))
        t.remove_all_term_tags()
        for tt in termtags:
            t.add_term_tag(tt)

        termparents = []
        lang = spec.language
        create_parents = [
            p
            for p in term.parents
            if p is not None
            and p != ""
            and lang.get_lowercase(term.text) != lang.get_lowercase(p)
        ]
        # print('creating parents: ' + ', '.join(create_parents))
        for p in create_parents:
            termparents.append(self._find_or_create_parent(p, lang, term, termtags))
        t.remove_all_parents()
        for tp in termparents:
            t.add_parent(tp)

        return t

    def _find_or_create_parent(self, pt, language, term, termtags) -> DBTerm:
        spec = self._search_spec_term(language.id, pt)
        p = DBTerm.find_by_spec(spec)

        if p is not None:
            if (p.translation or "") == "":
                p.translation = term.translation
            if (p.get_current_image() or "") == "":
                p.set_current_image(term.current_image)
            return p

        p = DBTerm(language, pt)
        p.status = term.status
        p.translation = term.translation
        p.set_current_image(term.current_image)
        for tt in termtags:
            p.add_term_tag(tt)

        return p

    def _build_business_term(self, dbterm):
        "Create a Term bus. object from a lute.model.term.Term."
        term = Term()
        term.id = dbterm.id
        term.language = dbterm.language
        term.language_id = dbterm.language.id

        # Remove zero-width spaces (zws) from strings for user forms.
        text = dbterm.text
        zws = "\u200B"  # zero-width space
        text = text.replace(zws, "")
        term.text_lc = dbterm.text_lc
        term.original_text = text
        term.text = text

        term.status = dbterm.status
        term.translation = dbterm.translation
        term.romanization = dbterm.romanization
        term.current_image = dbterm.get_current_image()
        term.flash_message = dbterm.get_flash_message()
        term.parents = [p.text for p in dbterm.parents]
        term.romanization = dbterm.romanization
        term.term_tags = [tt.text for tt in dbterm.term_tags]

        return term

    ## References.

    def find_references(self, term):
        """
        Return references of term, children, and parents.
        """
        spec = self._search_spec_term(term.language_id, term.text)
        searchterm = DBTerm.find_by_spec(spec)
        if searchterm is None:
            searchterm = spec

        references = {
            "term": self._get_references(searchterm),
            "children": self._get_child_references(searchterm),
            "parents": self._get_parent_references(searchterm),
        }
        return references

    def _build_term_references(self, term_lc, rows):
        ret = []
        zws = chr(0x200B)  # zero-width space
        for row in rows:
            sentence = row[4].strip()
            pattern = f"{zws}({term_lc}){zws}"

            def replace_match(m):
                return f"{zws}<b>{m.group(0)}</b>{zws}"

            sentence = re.sub(pattern, replace_match, sentence, flags=re.IGNORECASE)
            sentence = sentence.replace(zws, "").replace("¶", "")
            ret.append(TermReference(row[0], row[1], row[2], row[3], sentence))
        return ret

    def _get_references(self, term):
        if term is None:
            return []

        term_lc = term.text_lc
        query = sqlalchtext(
            """
            SELECT DISTINCT
                texts.TxBkID,
                TxID,
                TxOrder,
                BkTitle || ' (' || TxOrder || '/' || pc.c || ')' AS TxTitle,
                SeText
            FROM sentences
            INNER JOIN texts ON TxID = SeTxID
            INNER JOIN books ON BkID = texts.TxBkID
            INNER JOIN (
                SELECT TxBkID, COUNT(*) AS c
                FROM texts
                GROUP BY TxBkID
            ) pc ON pc.TxBkID = texts.TxBkID
            WHERE TxReadDate IS NOT NULL
            AND LOWER(SeText) LIKE :pattern
            LIMIT 20
        """
        )

        pattern = f"%{chr(0x200B)}{term_lc}{chr(0x200B)}%"
        params = {"pattern": pattern}
        result = self.db.session.execute(query, params)
        return self._build_term_references(term_lc, result)

    def _get_all_refs(self, terms):
        all_references = []
        for term in terms:
            references = self._get_references(term)
            all_references.extend(references)
        return all_references

    def _get_parent_references(self, term):
        parent_references = []
        for parent in term.parents:
            parent_term_lc = parent.text_lc
            references = self._get_family_references(parent, term)
            parent_references.append({"term": parent_term_lc, "refs": references})
        return parent_references

    def _get_family_references(self, parent, term):
        if term is None or parent is None:
            return []
        family = [parent] + parent.children
        family = [t for t in family if t.id != term.id]
        return self._get_all_refs(family)

    def _get_child_references(self, term):
        if term is None:
            return []
        return self._get_all_refs(term.children)
