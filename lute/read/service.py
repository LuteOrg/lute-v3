"""
Reading helpers.
"""

import functools
from lute.models.term import Term, Status
from lute.models.book import Text
from lute.book.stats import mark_stale
from lute.read.render.service import get_paragraphs, find_all_Terms_in_string
from lute.read.render.renderable_calculator import TokenLocator
from lute.term.model import Repository
from lute.db import db

# from lute.utils.debug_helpers import DebugTimer


def set_unknowns_to_known(text: Text):
    """
    Given a text, create new Terms with status Well-Known
    for any new Terms.
    """
    paragraphs = get_paragraphs(text.text, text.book.language)
    _save_new_status_0_terms(paragraphs)

    unknowns = [
        ti.term
        for para in paragraphs
        for sentence in para
        for ti in sentence.textitems
        if ti.is_word and ti.term.status == 0
    ]

    batch_size = 100
    i = 0

    for t in unknowns:
        t.status = Status.WELLKNOWN
        db.session.add(t)
        i += 1
        if i % batch_size == 0:
            db.session.commit()

    # Commit any remaining.
    db.session.commit()


def bulk_status_update(text: Text, terms_text_array, new_status):
    """
    Given a text and list of terms, update or create new terms
    and set the status.
    """
    language = text.book.language
    repo = Repository(db)
    for term_text in terms_text_array:
        t = repo.find_or_new(language.id, term_text)
        t.status = new_status
        repo.add(t)
    repo.commit()


def _save_new_status_0_terms(paragraphs):
    "Add status 0 terms for new textitems in paragraph."
    tis_with_new_terms = [
        ti
        for para in paragraphs
        for sentence in para
        for ti in sentence.textitems
        if ti.is_word and ti.term.id is None and ti.term.status == 0
    ]

    for ti in tis_with_new_terms:
        db.session.add(ti.term)
    db.session.commit()


def start_reading(dbbook, pagenum, db_session):
    "Start reading a page in the book, getting paragraphs."

    text = dbbook.text_at_page(pagenum)
    text.load_sentences()

    mark_stale(dbbook)
    dbbook.current_tx_id = text.id
    db_session.add(dbbook)
    db_session.add(text)
    db_session.commit()

    lang = text.book.language
    paragraphs = get_paragraphs(text.text, lang)
    _save_new_status_0_terms(paragraphs)

    return paragraphs


def get_popup_data(termid):
    "Get the data necessary to render a term popup."
    term = Term.find(termid)

    term_tags = [tt.text for tt in term.term_tags]

    def make_array(t):
        ret = {
            "term": t.text,
            "roman": t.romanization,
            "trans": t.translation if t.translation else "-",
            "tags": [tt.text for tt in t.term_tags],
        }
        return ret

    parent_terms = [p.text for p in term.parents]
    parent_terms = ", ".join(parent_terms)

    parents = term.parents
    if len(parents) == 1 and parents[0].translation == term.translation:
        parents = []
    parent_data = [make_array(p) for p in parents]

    def sort_components(components):
        # Sort components by min position in string and length.
        subj = TokenLocator.make_string(term.text)
        tocloc = TokenLocator(term.language, subj)
        component_and_pos = []
        for c in components:
            locs = tocloc.locate_string(c.text)
            # pylint: disable=consider-using-generator
            index = min([loc["index"] for loc in locs])
            component_and_pos.append([c, index])

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

    components = [
        c for c in find_all_Terms_in_string(term.text, term.language) if c.id != term.id
    ]
    components = sort_components(components)

    component_data = [make_array(c) for c in components]
    component_data = [c for c in component_data if c["trans"] != "-"]

    images = [term.get_current_image()] if term.get_current_image() else []
    for p in term.parents:
        if p.get_current_image():
            images.append(p.get_current_image())
    # DISABLED CODE: Don't include component images in the hover for now,
    # it can get confusing!
    # ref https://github.com/LuteOrg/lute-v3/issues/355
    # for c in components:
    #     if c.get_current_image():
    #         images.append(c.get_current_image())

    images = list(set(images))

    return {
        "term": term,
        "flashmsg": term.get_flash_message(),
        "term_tags": term_tags,
        "term_images": images,
        "parentdata": parent_data,
        "parentterms": parent_terms,
        "components": component_data,
    }
