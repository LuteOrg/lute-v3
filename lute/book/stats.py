"""
Book statistics.
"""

from lute.read.service import get_paragraphs

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
        get_paragraphs(t) for t in
        # Next 20 pages, a good enough sample.
        book.texts[txindex:txindex + 20]
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

    statterms = {
        0: [],
        1: [],
        2: [],
        3: [],
        4: [],
        5: [],
        98: [],
        99: []
    }

    for ti in text_items:
        statterms[ti.wo_status or 0].append(ti.text_lc)

    stats = {}
    for statusval, allterms in statterms.items():
        uniques = list(set(allterms))
        statterms[statusval] = uniques
        stats[statusval] = len(uniques)

    return stats
