"""
Data cleanup routines.

Sometimes required as data management changes.
These cleanup routines will be called by the app_factory.
"""

from lute.models.book import Text


class ProgressReporter:
    "Report progress for to an output function."

    def __init__(self, total_count, output_func, report_every=100):
        "Setup counters."
        self.current = 0
        self.last_output = 0
        self.total_count = total_count
        self.report_every = report_every
        self.output_func = output_func

    def increment(self):
        "Increment counter, and if past threshold, output."
        if self.total_count == 0:
            return
        self.current += 1
        if self.current - self.last_output < self.report_every:
            return
        self.output_func(f"  {self.current} of {self.total_count}")
        self.last_output = self.current


def _set_texts_word_count(session, output_function):
    """
    texts.TxWordCount should be set for all texts.

    Fixing a design error: the counts should have been stored here,
    instead of only in books.BkWordCount.

    Ref https://github.com/jzohrab/lute-v3/issues/95
    """
    calc_counts = session.query(Text).filter(Text.word_count.is_(None)).all()

    # Don't recalc with invalid parsers!!!!
    recalc = [t for t in calc_counts if t.book.language.is_supported]

    if len(recalc) == 0:
        # Nothing to calculate, quit.
        return

    output_function(f"Fixing word counts for {len(recalc)} Texts.")
    pr = ProgressReporter(len(recalc), output_function)
    for t in recalc:
        pr.increment()
        pt = t.book.language.get_parsed_tokens(t.text)
        words = [w for w in pt if w.is_word]
        t.word_count = len(words)
        session.add(t)
    session.commit()
    output_function("Done.")


def clean_data(session, output_function):
    "Clean all data as required, sending messages to output_function."
    _set_texts_word_count(session, output_function)
