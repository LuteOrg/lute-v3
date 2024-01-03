"""
Book statistics.
"""

import json
from lute.read.service import get_paragraphs
from lute.db import db
from lute.models.book import Book


def get_unique_words(book, numpages):
    """
    Return count of unique words with statuses for the next numpages
    """
    txindex = 0
    words_dict = {}

    if (book.current_tx_id or 0) != 0:
        for t in book.texts:
            if t.id == book.current_tx_id:
                break
            txindex += 1

    for text in book.texts[txindex : txindex + numpages]:
        for paragraph in get_paragraphs(text):
            for sentence in paragraph:
                for word in sentence.textitems:
                    if word.is_word:
                        word_lc = word.text_lc
                        if word_lc not in words_dict.keys():
                            words_dict.update({word_lc: word.wo_status})

    return words_dict


def get_status_distribution(words_dict):
    """
    Return the status distribution for given unique words
    """
    stats = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 98: 0, 99: 0}
    for word in words_dict:
        stats[words_dict[word] or 0] += 1

    return stats


##################################################
# Stats table refresh.


class BookStats(db.Model):
    "The stats table."
    __tablename__ = "bookstats"

    id = db.Column(db.Integer, primary_key=True)
    BkID = db.Column(db.Integer)
    wordcount = db.Column(db.Integer)
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
    """
    Calc stats for the book using the status distribution.
    Do a full render of the next 20 pages in a book
    to calculate the distribution.
    """
    words_dict = get_unique_words(book, 20)
    unique_words = words_dict.keys()
    status_distribution = get_status_distribution(words_dict)
    unknowns = status_distribution[0]
    unique_words_count = len(unique_words)

    percent = 0
    if unique_words_count > 0:  # In case not parsed.
        percent = round(100.0 * unknowns / unique_words_count)

    status_distribution[99] = status_distribution[98] + status_distribution[99]
    status_distribution.pop(98)

    percentages = {}
    for status in status_distribution:
        pct = (status_distribution[status] / unique_words_count) * 100
        percentages.update({status: pct})

    sd = json.dumps(percentages)

    # Any change in the below fields requires a change to
    # update_stats as well, query insert doesn't check field order.
    return [book.word_count or 0, unique_words_count, unknowns, percent, sd]


def _update_stats(book, stats):
    "Update BookStats for the given book."
    new_stats = BookStats(
        BkID=book.id,
        wordcount=stats[0],
        distinctterms=stats[1],
        distinctunknowns=stats[2],
        unknownpercent=stats[3],
        status_distribution=stats[4],
    )
    db.session.add(new_stats)
    db.session.commit()
