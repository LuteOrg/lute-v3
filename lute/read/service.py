"""
Reading helpers.
"""

from collections import defaultdict
from datetime import datetime
import functools
from lute.models.term import Term, Status
from lute.models.book import Text, WordsRead
from lute.models.repositories import BookRepository
from lute.book.stats import Service as StatsService
from lute.read.render.service import Service as RenderService
from lute.read.render.calculate_textitems import get_string_indexes
from lute.term.model import Repository

# from lute.utils.debug_helpers import DebugTimer


class Service:
    "Service."

    def __init__(self, session):
        self.session = session

    def mark_page_read(self, bookid, pagenum, mark_rest_as_known):
        "Mark page as read, record stats, rest as known."
        br = BookRepository(self.session)
        book = br.find(bookid)
        text = book.text_at_page(pagenum)
        d = datetime.now()
        text.read_date = d
        w = WordsRead(text, d, text.word_count)
        self.session.add(text)
        self.session.add(w)
        self.session.commit()
        if mark_rest_as_known:
            self.set_unknowns_to_known(text)

    def set_unknowns_to_known(self, text: Text):
        """
        Given a text, create new Terms with status Well-Known
        for any new Terms.
        """
        rs = RenderService(self.session)
        paragraphs = rs.get_paragraphs(text.text, text.book.language)
        self._save_new_status_0_terms(paragraphs)

        unknowns = [
            ti.term
            for para in paragraphs
            for sentence in para
            for ti in sentence
            if ti.is_word and ti.term.status == 0
        ]

        batch_size = 100
        i = 0

        for t in unknowns:
            t.status = Status.WELLKNOWN
            self.session.add(t)
            i += 1
            if i % batch_size == 0:
                self.session.commit()

        # Commit any remaining.
        self.session.commit()

    def bulk_status_update(self, text: Text, terms_text_array, new_status):
        """
        Given a text and list of terms, update or create new terms
        and set the status.
        """
        language = text.book.language
        repo = Repository(self.session)
        for term_text in terms_text_array:
            t = repo.find_or_new(language.id, term_text)
            t.status = new_status
            repo.add(t)
        repo.commit()

    def _save_new_status_0_terms(self, paragraphs):
        "Add status 0 terms for new textitems in paragraph."
        tis_with_new_terms = [
            ti
            for para in paragraphs
            for sentence in para
            for ti in sentence
            if ti.is_word and ti.term.id is None and ti.term.status == 0
        ]

        for ti in tis_with_new_terms:
            self.session.add(ti.term)
        self.session.commit()

    def start_reading(self, dbbook, pagenum):
        "Start reading a page in the book, getting paragraphs."

        text = dbbook.text_at_page(pagenum)
        text.load_sentences()

        svc = StatsService(self.session)
        svc.mark_stale(dbbook)
        dbbook.current_tx_id = text.id
        self.session.add(dbbook)
        self.session.add(text)
        self.session.commit()

        lang = text.book.language
        rs = RenderService(self.session)
        paragraphs = rs.get_paragraphs(text.text, lang)
        self._save_new_status_0_terms(paragraphs)

        return paragraphs

    def _get_popup_image_data(self, terms):
        "Get images"
        # Don't include component images in the hover for now,
        # it can get confusing!
        # ref https://github.com/LuteOrg/lute-v3/issues/355
        images = [
            (t.get_current_image(), t.text) for t in terms if t.get_current_image()
        ]
        imageresult = defaultdict(list)
        for key, value in images:
            imageresult[key].append(value)
        # Convert lists to comma-separated strings
        return {k: ", ".join(v) for k, v in imageresult.items()}

    def _sort_components(self, term, components):
        "Sort components by min position in string and length."
        component_and_pos = []
        for c in components:
            c_indices = [
                loc[1] for loc in get_string_indexes([c.text_lc], term.text_lc)
            ]

            # Sometimes the components aren't found
            # in the string, which makes no sense ...
            # ref https://github.com/LuteOrg/lute-v3/issues/474
            if len(c_indices) > 0:
                component_and_pos.append([c, min(c_indices)])

        def compare(a, b):
            # Lowest position (closest to front of string) sorts first.
            if a[1] != b[1]:
                return -1 if (a[1] < b[1]) else 1
            # Longest sorts first.
            alen = len(a[0].text)
            blen = len(b[0].text)
            return -1 if (alen > blen) else 1

        component_and_pos.sort(key=functools.cmp_to_key(compare))
        return [c[0] for c in component_and_pos]

    def get_popup_data(self, termid):
        "Get popup data, or None if popup shouldn't be shown."
        term = self.session.get(Term, termid)
        if term is None:
            return None

        rs = RenderService(self.session)
        components = [
            c
            for c in rs.find_all_Terms_in_string(term.text, term.language)
            if c.id != term.id and c.status != Status.UNKNOWN
        ]

        def has_popup_data(cterm):
            return (
                (cterm.translation or "").strip() != ""
                or (cterm.romanization or "").strip() != ""
                or cterm.get_current_image() is not None
                or len(cterm.term_tags) != 0
            )

        if not has_popup_data(term) and len(term.parents) == 0 and len(components) == 0:
            return None

        translation = (term.translation or "").strip()

        def make_array(t):
            ret = {
                "term": t.text,
                "roman": (t.romanization or "").strip(),
                "trans": (t.translation or "").strip(),
                "tags": [tt.text for tt in t.term_tags],
            }
            return ret

        parent_data = [make_array(p) for p in term.parents]

        if len(parent_data) == 1:
            ptrans = parent_data[0]["trans"]
            if translation == "":
                translation = ptrans
            if translation == ptrans:
                parent_data[0]["trans"] = ""

        component_data = [
            make_array(c) for c in self._sort_components(term, components)
        ]

        def arr_has_popup_data(arr):
            checks = [arr["roman"] != "", arr["trans"] != "", len(arr["tags"]) > 0]
            return len([b for b in checks if b]) > 0

        ret = {
            "term": term,
            "flashmsg": term.get_flash_message(),
            "term_tags": [tt.text for tt in term.term_tags],
            "term_translation": translation,
            "term_images": self._get_popup_image_data([term, *term.parents]),
            "parentdata": [p for p in parent_data if arr_has_popup_data(p)],
            "parentterms": ", ".join([p.text for p in term.parents]),
            "components": [c for c in component_data if arr_has_popup_data(c)],
        }
        # print(ret, flush=True)
        return ret
