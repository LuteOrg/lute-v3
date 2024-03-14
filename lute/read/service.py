"""
Reading helpers.
"""

from lute.models.term import Term, Status
from lute.models.book import Text
from lute.book.stats import mark_stale
from lute.read.render.service import get_paragraphs
from lute.term.model import Repository

from lute.db import db


def set_unknowns_to_known(text: Text):
    """
    Given a text, create new Terms with status Well-Known
    for any new Terms.
    """
    language = text.book.language

    sentences = sum(get_paragraphs(text.text, text.book.language), [])

    tis = []
    for sentence in sentences:
        for ti in sentence.textitems:
            tis.append(ti)

    def is_unknown(ti):
        return (
            ti.is_word == 1
            and (ti.wo_id == 0 or ti.wo_id is None)
            and ti.token_count == 1
        )

    unknowns = list(filter(is_unknown, tis))
    words_lc = [ti.text_lc for ti in unknowns]
    uniques = list(set(words_lc))
    uniques.sort()

    batch_size = 100
    i = 0

    # There is likely a better way to write this using generators and
    # yield.
    for u in uniques:
        candidate = Term(language, u)
        t = Term.find_by_spec(candidate)
        if t is None:
            candidate.status = Status.WELLKNOWN
            db.session.add(candidate)
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


def start_reading(dbbook, pagenum, db_session):
    "Start reading a page in the book, getting paragraphs."

    text = dbbook.text_at_page(pagenum)
    text.load_sentences()

    mark_stale(dbbook)
    dbbook.current_tx_id = text.id
    db_session.add(dbbook)
    db_session.add(text)
    db_session.commit()

    paragraphs = get_paragraphs(text.text, text.book.language)

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

    parent_data = []
    if len(term.parents) == 1:
        parent = term.parents[0]
        if parent.translation != term.translation:
            parent_data.append(make_array(parent))
    else:
        parent_data = [make_array(p) for p in term.parents]

    images = [term.get_current_image()] if term.get_current_image() else []
    for p in term.parents:
        if p.get_current_image():
            images.append(p.get_current_image())

    images = list(set(images))

    return {
        "term": term,
        "flashmsg": term.get_flash_message(),
        "term_tags": term_tags,
        "term_images": images,
        "parentdata": parent_data,
        "parentterms": parent_terms,
    }
