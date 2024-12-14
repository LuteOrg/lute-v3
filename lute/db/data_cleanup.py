"""
Data cleanup routines.

Sometimes required as data management changes.
These cleanup routines will be called by the app_factory.
"""

from sqlalchemy import text as sqltext
from lute.models.language import Language
from lute.models.book import Text, Sentence


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


def _load_sentence_textlc(session, output_function):
    """
    sentences.SeTextLC was added after deployment, need to load it
    to fix issue 531.  ref https://github.com/LuteOrg/lute-v3/issues/531

    Only update sentences where the language is supported.  e.g. the
    user may have installed mecab, done some japanese, and then
    uninstalled mecab: the data will be hidden, but it's still
    present, and the sentences cannot be updated as the parser can't
    be loaded.
    """

    supported_langs = {
        lang.id: lang for lang in session.query(Language).all() if lang.is_supported
    }
    langids = [f"{k}" for k in list(supported_langs.keys())]
    if len(langids) == 0:
        langids = ["-999"]  # dummy to ensure good base sql

    base_sql = f"""
    select SeID, BkLgID
    from sentences
    inner join texts on SeTxID = TxID
    inner join books on BkID = TxBkID
    where BkLgID in ({','.join(langids)})
    and SeTextLC is null
    """

    count = session.execute(sqltext(f"select count(*) from ({base_sql}) src")).scalar()
    if count == 0:
        # Do nothing, don't print messages."
        return

    def _get_next_batch(batch_size):
        # Query for up to 1000 Sentence objects where textlc_content is None
        sql = f"{base_sql} limit {batch_size}"
        recs = session.execute(sqltext(sql)).all()
        seids = [int(rec[0]) for rec in recs]
        if len(seids) == 0:
            return []

        sentences = session.query(Sentence).filter(Sentence.id.in_(seids)).all()
        se_map = {se.id: se for se in sentences}
        return [
            {"sentence": se_map[int(rec[0])], "langid": int(rec[1])} for rec in recs
        ]

    # Guard against infinite loop.
    last_batch_ids = []

    output_function(f"Updating data for {count} sentences.")
    batch_size = 1000
    pr = ProgressReporter(count, output_function, report_every=batch_size)
    batch = _get_next_batch(batch_size)
    while len(batch) > 0:
        curr_batch_ids = [se_langid["sentence"].id for se_langid in batch]
        if last_batch_ids == curr_batch_ids:
            raise RuntimeError("Sentences not getting updated correctly.")

        for se_langid in batch:
            pr.increment()
            sentence = se_langid["sentence"]
            lang = supported_langs[se_langid["langid"]]
            if lang is None:
                raise RuntimeError(f"Logic err: Missing langid={se_langid['langid']}")
            sentence.set_lowercase_text(lang.parser)
            session.add(sentence)
        session.commit()

        last_batch_ids = curr_batch_ids
        batch = _get_next_batch(batch_size)

    session.commit()
    output_function("Done.")


def clean_data(session, output_function):
    "Clean all data as required, sending messages to output_function."
    _set_texts_word_count(session, output_function)
    _load_sentence_textlc(session, output_function)
