"""
Book statistics.
"""

import json
from lute.read.render.service import get_paragraphs
from lute.db import db
from lute.models.book import Book


def _last_5_pages(book, txindex):
    "Get next 5 pages, or at least 5 pages."
    start_index = max(0, txindex - 5)
    end_index = txindex + 5
    texts = book.texts[start_index:end_index]
    return texts[-5:]


def get_status_distribution(book):
    """
    Return statuses and count of unique words per status.

    Does a full render of a small number of pages
    to calculate the distribution.
    """
    txindex = 0

    if (book.current_tx_id or 0) != 0:
        for t in book.texts:
            if t.id == book.current_tx_id:
                break
            txindex += 1

    # get next 5 pages, a good enough sample ...
    # min 5 pages.
    text_sample = [t.text for t in _last_5_pages(book, txindex)]
    text_sample = "\n".join(text_sample)

    paras = get_paragraphs(text_sample, book.language)

    def flatten_list(nested_list):
        result = []
        for item in nested_list:
            if isinstance(item, list):
                result.extend(flatten_list(item))
            else:
                result.append(item)
        return result

    text_items = []
    for s in flatten_list(paras):
        text_items.extend(s.textitems)
    text_items = [ti for ti in text_items if ti.is_word]

    statterms = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 98: [], 99: []}

    for ti in text_items:
        statterms[ti.wo_status or 0].append(ti.text_lc)

    stats = {}
    for statusval, allterms in statterms.items():
        uniques = list(set(allterms))
        statterms[statusval] = uniques
        stats[statusval] = len(uniques)

    return stats


##################################################
# Stats table refresh.


class BookStats(db.Model):
    "The stats table."
    __tablename__ = "bookstats"

    id = db.Column(db.Integer, primary_key=True)
    BkID = db.Column(db.Integer)
    distinctterms = db.Column(db.Integer)
    distinctunknowns = db.Column(db.Integer)
    unknownpercent = db.Column(db.Integer)
    status_distribution = db.Column(db.String, nullable=True)


def refresh_stats():
    "Refresh stats for all books requiring update."
    books_to_update = (
        db.session.query(Book)
        .filter(~Book.id.in_(db.session.query(BookStats.BkID)))
        .all()
    )
    books = [b for b in books_to_update if b.is_supported]
    for book in books:
        stats = _get_stats(book)
        _update_stats(book, stats)


def mark_stale(book):
    "Mark a book's stats as stale to force refresh."
    bk_id = book.id
    db.session.query(BookStats).filter_by(BkID=bk_id).delete()
    db.session.commit()


def _get_stats(book):
    "Calc stats for the book using the status distribution."
    status_distribution = get_status_distribution(book)
    unknowns = status_distribution[0]
    allunique = sum(status_distribution.values())

    percent = 0
    if allunique > 0:  # In case not parsed.
        percent = round(100.0 * unknowns / allunique)

    sd = json.dumps(status_distribution)

    # Any change in the below fields requires a change to
    # update_stats as well, query insert doesn't check field order.
    return [allunique, unknowns, percent, sd]


def _update_stats(book, stats):
    "Update BookStats for the given book."
    new_stats = BookStats(
        BkID=book.id,
        distinctterms=stats[0],
        distinctunknowns=stats[1],
        unknownpercent=stats[2],
        status_distribution=stats[3],
    )
    db.session.add(new_stats)
    db.session.commit()
