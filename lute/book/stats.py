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
    start_text_index = 0

    curr_tx_id = book.current_tx_id
    if curr_tx_id != 0 and curr_tx_id is not None:
        for t in book.texts:
            if t.id == curr_tx_id:
                break
            start_text_index += 1

    # Get the next 20 pages, a good enough sample.
    end_ind = start_text_index + 20
    texts = book.texts[start_text_index:end_ind]
    paras = [ get_paragraphs(t) for t in texts ]

    def flatten_list(nested_list):
        result = []
        for item in nested_list:
            if isinstance(item, list):
                result.extend(flatten_list(item))
            else:
                result.append(item)
        return result
    sentences = flatten_list(paras)
    text_items = []
    for s in sentences:
        sent_words = [ti for ti in s.textitems if ti.is_word]
        text_items.extend(sent_words)

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
    for statusval in statterms.keys():
        allterms = statterms[statusval]
        uniques = list(set(allterms))
        statterms[statusval] = uniques
        stats[statusval] = len(uniques)

    return stats
