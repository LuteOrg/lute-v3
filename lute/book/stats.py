"""
Book statistics.
"""

from lute.read.service import get_paragraphs
from lute.db import db
from lute.models.book import Book


def get_status_distribution(book):
    """
    Return statuses and count of unique words per status.

    Does a full render of the next 20 pages in a book
    to calculate the distribution.
    """
    txindex = 0

    if (book.current_tx_id or 0) != 0:
        for t in book.texts:
            if t.id == book.current_tx_id:
                break
            txindex += 1

    paras = [
        get_paragraphs(t)
        for t in
        # Next 20 pages, a good enough sample.
        book.texts[txindex : txindex + 20]
    ]

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


def get_status_distribution2(book):
    """
    Return statuses and count of unique words per status.

    Does a full render of the next 20 pages in a book
    to calculate the distribution.
    """
    txindex = 0
    words = {}
    stats = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 98: 0, 99: 0}

    if (book.current_tx_id or 0) != 0:
        for t in book.texts:
            if t.id == book.current_tx_id:
                break
            txindex += 1

    for text in book.texts[txindex : txindex + 20]:
        for paragraph in get_paragraphs(text):
            for sentence in paragraph:
                for word in sentence.textitems:
                    if word.is_word:
                        words.update({word.text_lc: word.wo_status})

    unique_words = list(set(list(words.keys())))
    for word in unique_words:
        stats[words[word] or 0] += 1

    return stats, unique_words


def get_book_status_fractions(book):
    status_distribution, unique_words = get_status_distribution2(book)
    # unique_words = len(unique_words) - status_distribution[99]
    # "ignored" regarded as "well known"
    # print(len(unique_words))
    # print("before", status_distribution[99])
    # print("before", status_distribution)
    status_distribution[99] = status_distribution[98] + status_distribution[99]

    # print("after", status_distribution[99])
    # print("after", status_distribution)
    status_distribution.pop(98)

    fractions = {}
    for status in status_distribution:
        fr = status_distribution[status] / len(unique_words)
        fractions.update({status: fr})

    # return [book.word_count or 0, unique_words, status_distribution[0], fractions]

    return {book.id: fractions}


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

    # Any change in the below fields requires a change to
    # update_stats as well, query insert doesn't check field order.
    return [book.word_count or 0, allunique, unknowns, percent]


def _update_stats(book, stats):
    "Update BookStats for the given book."
    new_stats = BookStats(
        BkID=book.id,
        wordcount=stats[0],
        distinctterms=stats[1],
        distinctunknowns=stats[2],
        unknownpercent=stats[3],
    )
    db.session.add(new_stats)
    db.session.commit()
