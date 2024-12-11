"""
Given text and Terms, determine what to render in the browser.

For example, given the following TextTokens A-I:

  A B C D E F G H I

And the following terms:

  "A" through "I" (single-word terms)
  "B C"       (term J)
  "E F G H I" (K)
  "F G"       (L)
  "C D E"     (M)

The following TextItems would be displayed on the reading screen,
with some of the Terms overlapping:

  [A][B C][-D E][-F G H I]
"""

import re
from collections import Counter
from lute.models.term import Term
from lute.read.render.text_item import TextItem

# from lute.utils.debug_helpers import DebugTimer

zws = "\u200B"  # zero-width space


def get_string_indexes(strings, content):
    """
    Returns list of arrays: [[string, index], ...]

    e.g., _get_string_indexes(["is a", "cat"], "here is a cat")
    returns [("is a", 1), ("cat", 3)].

    strings and content must be lowercased!
    """
    searchcontent = zws + content + zws
    zwsindexes = [index for index, letter in enumerate(searchcontent) if letter == zws]

    ret = []

    for s in strings:
        # "(?=())" is required because sometimes the search pattern can
        # overlap -- e.g. _b_b_ has _b_ *twice*.
        # https://stackoverflow.com/questions/5616822/
        #   how-to-use-regex-to-find-all-overlapping-matches
        pattern = rf"(?=({re.escape(zws + s + zws)}))"
        add_matches = [
            (s, zwsindexes.index(m.start()))
            for m in re.finditer(pattern, searchcontent)
        ]
        ret.extend(add_matches)

    return ret


# pylint: disable=too-many-arguments,too-many-positional-arguments
def _make_textitem(index, text, text_lc, count, sentence_number, term):
    "Make a TextItem."
    r = TextItem()
    r.text = text
    r.sentence_number = sentence_number
    r.text_lc = text_lc
    r.token_count = count
    r.display_count = r.token_count
    r.index = index
    r.is_word = term is not None
    r.term = term
    return r


def _create_missing_status_0_terms(tokens, terms, language):
    "Make new terms as needed for all tokens, using case of last instance."

    original_word_tokens = {t.token for t in tokens if t.is_word}
    parser = language.parser
    lc_word_tokens = {parser.get_lowercase(t): t for t in original_word_tokens}
    term_text_lcs = {t.text_lc for t in terms}

    missing_word_tokens = [
        original for lc, original in lc_word_tokens.items() if lc not in term_text_lcs
    ]

    # Note: create the terms _without parsing_ because some parsers
    # break up characters when the words are given out of context.
    missing_word_tokens = list(set(missing_word_tokens))
    new_terms = [Term.create_term_no_parsing(language, t) for t in missing_word_tokens]
    for t in new_terms:
        t.status = 0

    return new_terms


def get_textitems(tokens, terms, language, multiword_term_indexer=None):
    """
    Return TextItems that will **actually be rendered**.

    Method to determine what should be rendered:

    - Create TextItems for all of the tokens, finding their
      starting index in the tokens.

    - "Write" the TextItems to an array in correctly sorted
      order, so that the correct TextItems take precendence
      in the final rendering.

    - Calculate any term overlaps.

    - Return the final list of TextItems that will actually
      be rendered.

    ---

    Applying the above algorithm to the example given in the class
    header:

    We have the following TextTokens A-I:

      A B C D E F G H I

    And given the following terms:
      "A" through "I" (single-word terms)
      "B C"       (term J)
      "E F G H I" (K)
      "F G"       (L)
      "C D E"     (M)

    Creating TextItems for all of the terms, finding their starting
    indices in the tokens:

      TextToken    index   length
      ----         -----   ------
      [A]          0       1
      [B]          1       1
      ...
      [I]          8       1
      [B C]        1       2
      [E F G H I]  4       5
      [F G]        5       2
      [C D E]      2       3

    Sorting by index, then decreasing token count:

      TextToken    index   length   ID (for later reference)
      ----         -----   ------   ------------------------
      [A]          0       1        t1
      [B C]        1       2        t2
      [B]          1       1        t3
      [C D E]      2       3        t4
      [C]          2       1        t5
      [D]          3       1        t6
      [E F G H I]  4       5        t7
      [E]          4       1        t8
      [F G]        5       2        t9
      [F]          5       1        t10
      [G]          6       1        t11
      [H]          7       1        t12
      [I]          8       1        t13

    Starting at the bottom of the above list and
    working upwards:

      - ID of [I] is written to index 8: [] [] [] [] [] [] [] [] [t13]
      - ID of [H] to index 7: [] [] [] [] [] [] [] [t12] [t13]
      - ...
      - [F G] to index 5 *and* 6: [] [] [] [] [] [t9] [t9] [t12] [t13]
      - [E] to index 4:  [] [] [] [] [t8] [t9] [t9] [t12] [t13]
      - [E F G H I] to indexes 4-8:   [] [] [] [] [t7] [t7] [t7] [t7] [t7]
      - ... etc

    Using the TextItem IDs, the resulting array would be:

      output array: [t1] [t2] [t2] [t4] [t4] [t7] [t7] [t7] [t7]
                    [A]  [B     C] [-D    E] [-F    G    H    I]

    The only TextItems that will be shown are therefore:
      t1, t2, t3, t7

    To calculate what text is actually displayed, the count
    of each ID is used.  e.g.:
      - ID t7 appears 4 times in the output array.  The last 4 tokens of
        [E F G H I] are [F G H I], which will be used as t7's display text.
      - ID t2 appears 2 times.  The last 2 tokens of [B C] are [B C],
        so that will be the display text. etc.
    """
    # pylint: disable=too-many-locals

    # dt = DebugTimer("get_textitems", display=False)

    new_unknown_terms = _create_missing_status_0_terms(tokens, terms, language)
    # dt.step("new_unknown_terms")

    all_terms = terms + new_unknown_terms
    text_to_term = {dt.text_lc: dt for dt in all_terms}

    tokens_orig = [t.token for t in tokens]
    tokens_lc = [language.parser.get_lowercase(t) for t in tokens_orig]

    textitems = []

    def _add_textitem(index, text_lc, count):
        "Add a TextItem for position index in tokens."
        text_orig = tokens_orig[index]
        if count > 1:
            text_orig = zws.join(tokens_orig[index : index + count])
        text_lc = zws.join(tokens_lc[index : index + count])
        sentence_number = tokens[index].sentence_number
        term = text_to_term.get(text_lc, None)
        ti = _make_textitem(index, text_orig, text_lc, count, sentence_number, term)
        textitems.append(ti)

    # Single-word terms.
    for index, _ in enumerate(tokens):
        _add_textitem(index, tokens_lc[index], 1)
    # dt.step("single word textitems")

    # Multiword terms.
    if multiword_term_indexer is not None:
        for r in multiword_term_indexer.search_all(tokens_lc):
            mwt = text_to_term[r[0]]
            count = mwt.token_count
            _add_textitem(r[1], r[0], count)
        # dt.step(f"get mw textitems w indexer")
    else:
        multiword_terms = [t.text_lc for t in all_terms if t.token_count > 1]
        for e in get_string_indexes(multiword_terms, zws.join(tokens_lc)):
            count = e[0].count(zws) + 1
            _add_textitem(e[1], e[0], count)
        # dt.step("mw textitems without indexer")

    # Sorting by index, then decreasing token count.
    textitems = sorted(textitems, key=lambda x: (x.index, -x.token_count))

    # "Write out" TextItems to the output array.
    output_textitem_ids = [None] * len(tokens)
    for ti in reversed(textitems):
        for c in range(ti.index, ti.index + ti.token_count):
            output_textitem_ids[c] = id(ti)

    # Calc display_counts; e.g. if a textitem's id shows up 3 times
    # in the output_textitem_ids, it should display 3 tokens.
    id_counts = dict(Counter(output_textitem_ids))
    for ti in textitems:
        ti.display_count = id_counts.get(id(ti), 0)
    # dt.step("display_count")

    textitems = [ti for ti in textitems if ti.display_count > 0]

    current_paragraph = 0
    for ti in textitems:
        ti.paragraph_number = current_paragraph
        if ti.text == "¶":
            current_paragraph += 1
    # dt.step("paragraphs")
    # dt.step("done")

    return textitems
