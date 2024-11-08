"""
Book statistics.
"""

import json
from sqlalchemy import select, text
from lute.read.render.service import Service as RenderService
from lute.models.book import Book, BookStats
from lute.models.repositories import UserSettingRepository

# from lute.utils.debug_helpers import DebugTimer


class Service:
    "Service."

    def __init__(self, session):
        self.session = session

    def _last_n_pages(self, book, txindex, n):
        "Get next n pages, or at least n pages."
        start_index = max(0, txindex - n)
        end_index = txindex + n
        texts = book.texts[start_index:end_index]
        return texts[-n:]

    def _get_sample_texts(self, book):
        "Get texts to use as sample."
        txindex = 0
        if (book.current_tx_id or 0) != 0:
            for t in book.texts:
                if t.id == book.current_tx_id:
                    break
                txindex += 1

        repo = UserSettingRepository(self.session)
        sample_size = int(repo.get_value("stats_calc_sample_size") or 5)
        texts = self._last_n_pages(book, txindex, sample_size)
        return texts

    def calc_status_distribution(self, book):
        """
        Calculate statuses and count of unique words per status.

        Does a full render of a small number of pages
        to calculate the distribution.
        """

        # DebugTimer.clear_total_summary()
        # dt = DebugTimer("get_status_distribution", display=False)
        texts = self._get_sample_texts(book)

        # Getting the individual paragraphs per page, and then combining,
        # is much faster than combining all pages into one giant page.
        service = RenderService(self.session)
        mw = service.get_multiword_indexer(book.language)
        textitems = []
        for tx in texts:
            textitems.extend(service.get_textitems(tx.text, book.language, mw))
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

    def refresh_stats(self):
        "Refresh stats for all books requiring update."
        sql = "delete from bookstats where status_distribution is null"
        self.session.execute(text(sql))
        self.session.commit()
        book_ids_with_stats = select(BookStats.BkID).scalar_subquery()
        books_to_update = (
            self.session.query(Book).filter(~Book.id.in_(book_ids_with_stats)).all()
        )
        books = [b for b in books_to_update if b.is_supported]
        for book in books:
            stats = self._calculate_stats(book)
            self._update_stats(book, stats)

    def mark_stale(self, book):
        "Mark a book's stats as stale to force refresh."
        bk_id = book.id
        self.session.query(BookStats).filter_by(BkID=bk_id).delete()
        self.session.commit()

    def get_stats(self, book):
        "Gets stats from the cache if available, or calculates."
        bk_id = book.id
        stats = self.session.query(BookStats).filter_by(BkID=bk_id).first()
        if stats is None or stats.status_distribution is None:
            newstats = self._calculate_stats(book)
            self._update_stats(book, newstats)
            stats = self.session.query(BookStats).filter_by(BkID=bk_id).first()
        return stats

    def _calculate_stats(self, book):
        "Calc stats for the book using the status distribution."
        status_distribution = self.calc_status_distribution(book)
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

    def _update_stats(self, book, stats):
        "Update BookStats for the given book."
        s = self.session.query(BookStats).filter_by(BkID=book.id).first()
        if s is None:
            s = BookStats(BkID=book.id)
        s.distinctterms = stats["allunique"]
        s.distinctunknowns = stats["unknowns"]
        s.unknownpercent = stats["percent"]
        s.status_distribution = stats["distribution"]
        self.session.add(s)
        self.session.commit()
