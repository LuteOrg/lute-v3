"""
Reading rendering helpers.
"""

import re
from sqlalchemy import text as sqltext

from lute.models.term import Term
from lute.parse.base import ParsedToken
from lute.read.render.renderable_calculator import RenderableCalculator
from lute.db import db


def find_all_Terms_in_string(s, language):  # pylint: disable=too-many-locals
    """
    Find all terms contained in the string s.

    For example
    - given s = "Here is a cat"
    - given terms in the db: [ "cat", "a cat", "dog" ]

    This would return the terms "cat" and "a cat".
    """

    cleaned = re.sub(r" +", " ", s)
    tokens = language.get_parsed_tokens(cleaned)
    return _find_all_terms_in_tokens(tokens, language)


def _find_all_terms_in_tokens(tokens, language):
    """
    Find all terms contained in the (ordered) parsed tokens tokens.

    For example
    - given tokens = "Here", " ", "is", " ", "a", " ", "cat"
    - given terms in the db: [ "cat", "a/ /cat", "dog" ]

    This would return the terms "cat" and "a/ /cat".

    The code first queries for exact single-token matches,
    and then multiword matches, because that's much faster
    than querying for everthing at once.  (This may no longer
    be true, can change it later.)
    """

    parser = language.parser

    # fyi - Manually searching for terms was slow (i.e., querying for
    # all terms, and checking if the strings were in the string s).

    # Query for terms with a single token that match the unique word tokens
    word_tokens = filter(lambda t: t.is_word, tokens)
    tok_strings = [parser.get_lowercase(t.token) for t in word_tokens]
    tok_strings = list(set(tok_strings))
    terms_matching_tokens = (
        db.session.query(Term)
        .filter(
            Term.language == language,
            Term.text_lc.in_(tok_strings),
            Term.token_count == 1,
        )
        .all()
    )

    # Multiword terms have zws between all tokens.
    # Create content string with zws between all tokens for the match.
    zws = "\u200B"  # zero-width space
    lctokens = [parser.get_lowercase(t.token) for t in tokens]
    content = zws + zws.join(lctokens) + zws

    sql = sqltext(
        """
        SELECT WoID FROM words
        WHERE WoLgID=:language_id and WoTokenCount>1
        AND :content LIKE '%' || :zws || WoTextLC || :zws || '%'
        """
    )
    sql = sql.bindparams(language_id=language.id, content=content, zws=zws)
    idlist = db.session.execute(sql).all()
    woids = [int(p[0]) for p in idlist]
    contained_terms = db.session.query(Term).filter(Term.id.in_(woids)).all()

    # Note that the above method (querying for ids, then getting terms)
    # is faster than using the model as shown below!
    ### contained_term_query = db.session.query(Term).filter(
    ###     Term.language == language,
    ###     Term.token_count > 1,
    ###     func.instr(content, Term.text_lc) > 0,
    ### )
    ### contained_terms = contained_term_query.all()

    return terms_matching_tokens + contained_terms


class RenderableSentence:
    """
    A collection of TextItems to be rendered.
    """

    def __init__(self, sentence_id, textitems):
        self.sentence_id = sentence_id
        self.textitems = textitems

    def __repr__(self):
        s = "".join([t.display_text for t in self.textitems])
        return f'<RendSent {self.sentence_id}, {len(self.textitems)} items, "{s}">'


## Getting paragraphs ##############################


def _split_tokens_by_paragraph(tokens):
    "Split tokens by ¶"
    ret = []
    curr_para = []
    for t in tokens:
        if t.token == "¶":
            ret.append(curr_para)
            curr_para = []
        else:
            curr_para.append(t)
    if len(curr_para) > 0:
        ret.append(curr_para)
    return ret


def _make_renderable_sentence(language, pnum, sentence_num, tokens, terms):
    """
    Make a RenderableSentences using the tokens present in
    that sentence.
    """
    sentence_tokens = [t for t in tokens if t.sentence_number == sentence_num]
    renderable = RenderableCalculator.get_renderable(language, terms, sentence_tokens)
    textitems = [i.make_text_item(pnum, sentence_num, language) for i in renderable]
    ret = RenderableSentence(sentence_num, textitems)
    return ret


def _sentence_nums(paratokens):
    "Sentence numbers in the paragraph tokens."
    senums = [t.sentence_number for t in paratokens]
    return sorted(list(set(senums)))


def _add_status_0_terms(paragraphs, lang):
    "Add status 0 terms for new textitems in paragraph."
    new_textitems = [
        ti
        for para in paragraphs
        for sentence in para
        for ti in sentence.textitems
        if ti.is_word and ti.term is None
    ]

    new_terms_needed = {t.text for t in new_textitems}
    new_terms = [Term.create_term_no_parsing(lang, t) for t in new_terms_needed]
    for t in new_terms:
        t.status = 0

    # new_terms may contain some dups (e.g. "cat" and "CAT" are both
    # created), so use a map with lowcase text to disambiguate.
    textlc_to_term_map = {t.text_lc: t for t in new_terms}
    for ti in new_textitems:
        ti.term = textlc_to_term_map[ti.text_lc]


def get_paragraphs(s, language):
    """
    Get array of arrays of RenderableSentences for the given string s.
    """
    # Hacky reset of state of ParsedToken state.
    # _Shouldn't_ be needed but doesn't hurt, even if it's lame.
    ParsedToken.reset_counters()

    cleaned = re.sub(r" +", " ", s)
    tokens = language.get_parsed_tokens(cleaned)

    # Brutal hack ... for some reason the tests fail in
    # CI, but _inconsistently_, with the token order numbers.  The
    # order sometimes jumps by 2 ... I really can't explain it.  So,
    # as a _complete hack_, I'm re-numbering the tokens now, to ensure
    # they're in order.
    tokens.sort(key=lambda x: x.order)
    if len(tokens) > 0:
        n = tokens[0].order
        for t in tokens:
            t.order = n
            n += 1

    terms = _find_all_terms_in_tokens(tokens, language)

    paragraphs = _split_tokens_by_paragraph(tokens)

    renderable_paragraphs = []
    pnum = 0
    for p in paragraphs:
        # A renderable paragraph is a collection of RenderableSentences.
        renderable_sentences = [
            _make_renderable_sentence(language, pnum, senum, p, terms)
            for senum in _sentence_nums(p)
        ]
        renderable_paragraphs.append(renderable_sentences)
        pnum += 1

    _add_status_0_terms(renderable_paragraphs, language)

    return renderable_paragraphs
