"""
Reading helpers.
"""

from lute.models.term import Term, Status
from lute.models.book import Text
from lute.book.stats import mark_stale
from lute.read.render.service import get_paragraphs, find_all_Terms_in_string
from lute.term.model import Repository
from lute.db import db

# from lute.utils.debug_helpers import DebugTimer


def set_unknowns_to_known(text: Text):
    """
    Given a text, create new Terms with status Well-Known
    for any new Terms.
    """
    language = text.book.language
    paragraphs = get_paragraphs(text.text, text.book.language)
    # Just in case.
    _add_status_0_terms(paragraphs, language)

    tis = [
        ti
        for para in paragraphs
        for sentence in para
        for ti in sentence.textitems
        if ti.is_word
    ]

    def is_unknown(ti):
        return ti.is_word == 1 and ti.term is not None and ti.wo_status == 0

    unknown_ids = [t.wo_id for t in tis if is_unknown(t)]
    uniques = list(set(unknown_ids))

    batch_size = 100
    i = 0

    for u in uniques:
        t = Term.find(u)
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


def _create_unknown_terms(textitems, lang):
    "Create any terms required for the page."
    # dt = DebugTimer("create-unk-terms")
    toks = [t.text for t in textitems]
    unique_word_tokens = list(set(toks))
    all_new_terms = [Term(lang, t) for t in unique_word_tokens]
    # dt.step("make all_new_terms")

    unique_text_lcs = {}
    for t in all_new_terms:
        if t.text_lc not in unique_text_lcs:
            unique_text_lcs[t.text_lc] = t
    unique_new_terms = unique_text_lcs.values()
    # dt.step("find unique_new_terms")

    for t in unique_new_terms:
        t.status = 0
        db.session.add(t)
    db.session.commit()
    # dt.step("commit")
    # dt.summary()

    return unique_new_terms


def _add_status_0_terms(paragraphs, lang):
    "Add status 0 terms for new textitems in paragraph."
    new_textitems = [
        ti
        for para in paragraphs
        for sentence in para
        for ti in sentence.textitems
        if ti.is_word and ti.term is None
    ]
    # Create new terms for all unknown word tokens in the text.
    new_terms = _create_unknown_terms(new_textitems, lang)

    # Set the terms for the unknown_textitems
    textlc_to_term_map = {}
    for t in new_terms:
        textlc_to_term_map[t.text_lc] = t
    for ti in new_textitems:
        ti.term = textlc_to_term_map[ti.text_lc]


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
    _add_status_0_terms(paragraphs, lang)

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

    components = [
        c for c in find_all_Terms_in_string(term.text, term.language) if c.id != term.id
    ]
    component_data = [make_array(c) for c in components]

    images = [term.get_current_image()] if term.get_current_image() else []
    for p in term.parents:
        if p.get_current_image():
            images.append(p.get_current_image())
    for c in components:
        if c.get_current_image():
            images.append(c.get_current_image())

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
