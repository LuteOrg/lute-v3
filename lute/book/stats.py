"""
Book statistics.
"""

import json
from lute.read.render.service import get_multiword_indexer, get_textitems
from lute.db import db
from lute.models.book import Book
from lute.models.setting import UserSetting

# from lute.utils.debug_helpers import DebugTimer


def _last_n_pages(book, txindex, n):
    "Get next n pages, or at least n pages."
    start_index = max(0, txindex - n)
    end_index = txindex + n
    texts = book.texts[start_index:end_index]
    return texts[-n:]


def calc_status_distribution(book):
    """
    Calculate statuses and count of unique words per status.

    Does a full render of a small number of pages
    to calculate the distribution.
    """

    # DebugTimer.clear_total_summary()
    # dt = DebugTimer("get_status_distribution", display=False)

    txindex = 0
    if (book.current_tx_id or 0) != 0:
        for t in book.texts:
            if t.id == book.current_tx_id:
                break
            txindex += 1

    sample_size = int(UserSetting.get_value("stats_calc_sample_size") or 5)
    texts = _last_n_pages(book, txindex, sample_size)

    # Getting the individual paragraphs per page, and then combining,
    # is much faster than combining all pages into one giant page.
    mw = get_multiword_indexer(book.language)
    textitems = []
    for tx in texts:
        textitems.extend(get_textitems(tx.text, book.language, mw))
    # # Old slower code:
    # text_sample = "\n".join([t.text for t in texts])
    # paras = get_paragraphs(text_sample, book.language) ... etc.
    # dt.step("get_paragraphs")

    textitems = [ti for ti in textitems if ti.is_word]
    statterms = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 98: [], 99: []}
    for ti in textitems:
        statterms[ti.wo_status or 0].append(ti.text_lc)

    stats = {}
    for statusval, allterms in statterms.items():
        uniques = list(set(allterms))
        statterms[statusval] = uniques
        stats[statusval] = len(uniques)

    # dt.step("compiled")
    # DebugTimer.total_summary()

    return stats


##################################################
# Stats table refresh.


class BookStats(db.Model):
    "The stats table."
    __tablename__ = "bookstats"

    BkID = db.Column(db.Integer, primary_key=True)
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
        stats = _calculate_stats(book)
        _update_stats(book, stats)


def mark_stale(book):
    "Mark a book's stats as stale to force refresh."
    bk_id = book.id
    db.session.query(BookStats).filter_by(BkID=bk_id).delete()
    db.session.commit()


def get_stats(book):
    "Gets stats from the cache if available, or calculates."
    bk_id = book.id
    stats = db.session.query(BookStats).filter_by(BkID=bk_id).first()
    if stats is None:
        newstats = _calculate_stats(book)
        _update_stats(book, newstats)
        stats = db.session.query(BookStats).filter_by(BkID=bk_id).first()
    return stats


def _calculate_stats(book):
    "Calc stats for the book using the status distribution."
    status_distribution = calc_status_distribution(book)
    unknowns = status_distribution[0]
    allunique = sum(status_distribution.values())

    percent = 0
    if allunique > 0:  # In case not parsed.
        percent = round(100.0 * unknowns / allunique)

    return {
        "allunique": allunique,
        "unknowns": unknowns,
        "percent": percent,
        "distribution": json.dumps(status_distribution),
    }


def _update_stats(book, stats):
    "Update BookStats for the given book."
    s = db.session.query(BookStats).filter_by(BkID=book.id).first()
    if s is None:
        s = BookStats(BkID=book.id)
    s.distinctterms = stats["allunique"]
    s.distinctunknowns = stats["unknowns"]
    s.unknownpercent = stats["percent"]
    s.status_distribution = stats["distribution"]
    db.session.add(s)
    db.session.commit()
