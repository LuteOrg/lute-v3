"""
Term business object and repository.

Terms are converted to and from lute.models.term.Term objects to save
them in the database.
"""

import re
import sqlalchemy

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
        self.sync_status = False
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

        Note that this does a search by the **tokenized version**
        of the text; i.e., first the text argument is converted into
        a "search specification" (spec) using the language with the given id.
        The db search is then done using this spec.  In most cases, this
        # will suffice.

        # In some cases, though, it may cause errors.  The parsing here is done
        # without a fuller context, which in some language parsers can result
        # in different results.  For example, the Japanese "集めれ" string can
        # can be parsed with mecab to return one unit ("集めれ") or two ("集め/れ"),
        # depending on context.

        # So what does this mean?  It means that any context-less searches
        # for terms that have ambiguous parsing results will, themselves,
        # also be ambiguous.  This impacts csv imports and term form usage.

        # For regular (reading screen) usage, it probably doesn't matter.
        # The terms in the reading screen are all created when the page is
        # opened, and so have ids assigned.  With that, terms are not
        # searched by text match, they are only searched by id.

        ## TODO verify_identity_map_comment:
        If it's new, don't add to the identity map ... it's not saved yet,
        and so if we search for it again we should hit the db again.

        # the above statement about the identity map was old code, and I'm not
        # sure it's a valid statement/condition.
        """
        t = self.find(langid, text)
        if t is not None:
            return t

        spec = self._search_spec_term(langid, text)
        t = Term()
        t.language = spec.language
        t.language_id = langid
        t.text = spec.text
        t.text_lc = spec.text_lc
        t.romanization = spec.language.parser.get_reading(text)
        t.original_text = spec.text

        # TODO verify_identity_map_comment
        # Adding the term to the map, even though it's new.
        self._add_to_identity_map(t)

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

        sql_query = """SELECT
        t.WoID as id,
        t.WoText as text,
        t.WoTextLC as text_lc,
        t.WoTranslation as translation,
        t.WoStatus as status,
        t.WoLgID as language_id,
        CASE WHEN wp.WpParentWoID IS NOT NULL THEN 1 ELSE 0 END AS has_children,
        CASE WHEN t.WoTextLC = :text_lc THEN 2
          WHEN t.WoTextLC LIKE :text_lc_starts_with THEN 1
          ELSE 0
        END as text_starts_with_search_string

        FROM words AS t
        LEFT JOIN (
          select WpParentWoID from wordparents group by WpParentWoID
        ) wp on wp.WpParentWoID = t.WoID

        WHERE t.WoLgID = :langid AND t.WoTextLC LIKE :text_lc_wildcard

        ORDER BY text_starts_with_search_string DESC, has_children DESC, t.WoTextLC
        LIMIT :max_results
        """
        # print(sql_query)
        params = {
            "text_lc": text_lc,
            "text_lc_wildcard": f"%{text_lc}%",
            "text_lc_starts_with": f"{text_lc}%",
            "langid": langid,
            "max_results": max_results,
        }
        # print(params)

        alchsql = sqlalchemy.text(sql_query)
        return self.db.session.execute(alchsql, params).fetchall()

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
        # print(f"in _build_db_term, term id = {term.id}", flush=True)
        if term.text is None:
            raise ValueError("Text not set for term")

        t = None
        if term.id is not None:
            # This is an existing term, so use it directly.
            t = DBTerm.find(term.id)
        else:
            # New term, or finding by text.
            spec = self._search_spec_term(term.language_id, term.text)
            t = DBTerm.find_by_spec(spec) or DBTerm()
            t.language = spec.language

        t.text = term.text
        t.original_text = term.text
        t.status = term.status
        t.translation = term.translation
        t.romanization = term.romanization
        t.sync_status = term.sync_status
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
        lang = t.language
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

        if len(termparents) != 1:
            t.sync_status = False

        # print(f"in _build_db_term, returning db term with term id = {t.id}", flush=True)
        return t

    def _find_or_create_parent(self, pt, language, term, termtags) -> DBTerm:
        spec = self._search_spec_term(language.id, pt)
        p = DBTerm.find_by_spec(spec)

        if p is not None:
            if p.status == 0:  # previously unknown, inherits from term.
                p.status = term.status
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

        text = dbterm.text
        ### Remove zero-width spaces (zws) from strings for user forms.
        ###
        ### NOTE: disabling this as it creates challenges for editing
        ### terms.  In some cases, the same term may have a zws
        ### character as part of it; in other cases, it won't, e.g. "
        ### 集めれ" sometimes is parsed as one token, and sometimes
        ### two ("集め/れ").  If we strip the zws from the string, then
        ### when it's posted back, Lute will think that it has changed.
        ### ... it gets messy.
        # zws = "\u200B"  # zero-width space
        # text = text.replace(zws, "")
        term.text_lc = dbterm.text_lc
        term.original_text = text
        term.text = text

        term.status = dbterm.status
        term.translation = dbterm.translation
        term.romanization = dbterm.romanization
        term.sync_status = dbterm.sync_status
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
        query = sqlalchemy.text(
            f"""
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
            AND BkLgID = {term.language.id}
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
