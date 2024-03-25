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
        AND :content LIKE '%' || WoTextLC || '%'
        """
    )
    sql = sql.bindparams(language_id=language.id, content=content)
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

    # Split into paragraphs.
    paragraphs = []
    curr_para = []
    for t in tokens:
        if t.token == "¶":
            paragraphs.append(curr_para)
            curr_para = []
        else:
            curr_para.append(t)
    if len(curr_para) > 0:
        paragraphs.append(curr_para)

    def make_RenderableSentence(pnum, sentence_num, tokens, terms):
        """
        Make a RenderableSentences using the tokens present in
        that sentence.  The current text and language are pulled
        into the function from the closure.
        """
        sentence_tokens = [t for t in tokens if t.sentence_number == sentence_num]
        renderable = RenderableCalculator.get_renderable(
            language, terms, sentence_tokens
        )
        textitems = [i.make_text_item(pnum, sentence_num, language) for i in renderable]
        ret = RenderableSentence(sentence_num, textitems)
        return ret

    def unique(arr):
        return list(set(arr))

    renderable_paragraphs = []
    pnum = 0
    for paratokens in paragraphs:
        # A renderable paragraph is a collection of RenderableSentences.
        renderable_sentences = [
            make_RenderableSentence(pnum, senum, paratokens, terms)
            for senum in sorted(unique([t.sentence_number for t in paratokens]))
        ]
        renderable_paragraphs.append(renderable_sentences)
        pnum += 1

    return renderable_paragraphs
