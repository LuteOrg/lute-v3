"""
Reading helpers.
"""

from collections import defaultdict
from datetime import datetime
import functools
from lute.models.term import Term, Status
from lute.models.book import Text, WordsRead
from lute.models.repositories import BookRepository, UserSettingRepository
from lute.book.stats import Service as StatsService
from lute.read.render.service import Service as RenderService
from lute.read.render.calculate_textitems import get_string_indexes
from lute.term.model import Repository

# from lute.utils.debug_helpers import DebugTimer


class TermPopup:
    "Popup data for a term."

    # pylint: disable=too-many-instance-attributes
    def __init__(self, term):
        self.term = term
        self.term_text = self._clean(term.text)
        self.parents_text = ", ".join([self._clean(p.text) for p in term.parents])
        self.translation = self._clean(term.translation)
        self.romanization = self._clean(term.romanization)
        self.tags = [tt.text for tt in term.term_tags]
        self.flash = self._clean(term.get_flash_message())
        self.image = term.get_current_image()
        self.popup_image_data = self._get_popup_image_data()

        # Final data to include in popup.
        self.parents = []
        self.components = []

    def _clean(self, t):
        "Clean text for popup usage."
        zws = "\u200B"
        ret = (t or "").strip()
        ret = ret.replace(zws, "")
        ret = ret.replace("\n", "<br />")
        return ret

    @property
    def show(self):
        "Calc if should show.  Must be deferred as values can be changed."
        checks = [self.romanization != "", self.translation != "", len(self.tags) > 0]
        return len([b for b in checks if b]) > 0

    def term_and_parents_text(self):
        "Return term text with parents if any."
        ret = self.term_text
        if self.parents_text != "":
            ret = f"{ret} ({self.parents_text})"
        return ret

    def _get_popup_image_data(self):
        "Get images"
        # Don't include component images in the hover for now,
        # it can get confusing!
        # ref https://github.com/LuteOrg/lute-v3/issues/355
        terms = [self.term, *self.term.parents]
        images = [
            (t.get_current_image(), t.text) for t in terms if t.get_current_image()
        ]
        imageresult = defaultdict(list)
        for key, value in images:
            imageresult[key].append(self._clean(value))
        # Convert lists to comma-separated strings
        return {k: ", ".join(v) for k, v in imageresult.items()}


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

    def _get_reading_data(self, dbbook, pagenum, track_page_open=False):
        "Get paragraphs, set text.start_date if needed."
        text = dbbook.text_at_page(pagenum)
        text.load_sentences()
        svc = StatsService(self.session)
        svc.mark_stale(dbbook)

        if track_page_open:
            text.start_date = datetime.now()
            dbbook.current_tx_id = text.id

        self.session.add(dbbook)
        self.session.add(text)
        self.session.commit()

        lang = text.book.language
        rs = RenderService(self.session)
        paragraphs = rs.get_paragraphs(text.text, lang)
        self._save_new_status_0_terms(paragraphs)

        return paragraphs

    def get_paragraphs(self, dbbook, pagenum):
        "Get the paragraphs for the book."
        return self._get_reading_data(dbbook, pagenum, False)

    def start_reading(self, dbbook, pagenum):
        "Start reading a page in the book, getting paragraphs."
        return self._get_reading_data(dbbook, pagenum, True)

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

        repo = UserSettingRepository(self.session)
        show_components = int(repo.get_value("term_popup_show_components")) == 1
        components = []
        if show_components:
            rs = RenderService(self.session)
            components = [
                c
                for c in rs.find_all_Terms_in_string(term.text, term.language)
                if c.id != term.id and c.status != Status.UNKNOWN
            ]

        t = TermPopup(term)
        if (
            t.show is False
            and t.image is None
            and len(term.parents) == 0
            and len(components) == 0
        ):
            # Nothing to show."
            return None

        parent_data = [TermPopup(p) for p in term.parents]

        promote_parent_trans = int(
            repo.get_value("term_popup_promote_parent_translation")
        )
        if (promote_parent_trans == 1) and len(term.parents) == 1:
            ptrans = parent_data[0].translation
            if t.translation == "":
                t.translation = ptrans
            if t.translation == ptrans:
                parent_data[0].translation = ""

        component_data = [TermPopup(c) for c in self._sort_components(term, components)]

        t.parents = [p for p in parent_data if p.show]
        t.components = [c for c in component_data if c.show]
        return t
