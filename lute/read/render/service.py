"""
Reading rendering helpers.
"""

import re
from sqlalchemy import text as sqltext

from lute.models.term import Term
from lute.parse.base import ParsedToken
from lute.read.render.renderable_calculator import RenderableCalculator
from lute.db import db

# from lute.utils.debug_helpers import DebugTimer


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
    than querying for everything at once.
    """

    # Future performance improvement considerations:
    #
    # 1. I considered keeping a cache of multiword terms strings and
    # IDs, but IMO the payoff isn't worth the extra complexity at this
    # time.
    #
    # 2. Maybe a different search method like Aho-Corasick (ref
    # https://github.com/abusix/ahocorapy) would be useful ... again
    # it would imply that all keywords (existing Terms) are loaded
    # into the Aho-Corasick automaton.  This could be cached, but would
    # again need methods for cache invalidation and reload etc.

    # dt = DebugTimer("_find_all_terms_in_tokens", False)

    parser = language.parser

    # Single word terms
    #
    # Build query for terms with a single token that match the unique
    # word tokens.  Note it's much faster to use a query for this,
    # rather than loading all term text and checking for the strings
    # using python, as we can rely on the database indexes.
    word_tokens = filter(lambda t: t.is_word, tokens)
    tok_strings = [parser.get_lowercase(t.token) for t in word_tokens]
    tok_strings = list(set(tok_strings))
    terms_matching_tokens_qry = db.session.query(Term).filter(
        Term.text_lc.in_(tok_strings), Term.language == language
    )
    # dt.step("single, query prep")

    # Multiword terms
    #
    # Multiword terms are harder to find as we have to do a full text
    # match.
    #
    # The "obvious" method of using the model is quite slow:
    #
    #   contained_term_qry = db.session.query(Term).filter(
    #     Term.language == language,
    #     Term.token_count > 1,
    #     func.instr(content, Term.text_lc) > 0,
    #   )
    #   contained_terms = contained_term_qry.all()
    #
    # This code first finds the IDs of the terms that are in the content,
    # and then loads the terms.
    #
    # Note that querying using 'LIKE' is again slow, i.e:
    #   sql = sqltext(
    #     """
    #     SELECT WoID FROM words
    #     WHERE WoLgID=:lid and WoTokenCount>1
    #     AND :content LIKE '%' || :zws || WoTextLC || :zws || '%'
    #     """
    #   )
    #   sql = sql.bindparams(lid=language.id, content=content, zws=zws)
    #
    # It is actually faster to load all Term text_lc and use python to
    # check if the strings are in the content string, and only then
    # load the terms.

    # Multiword terms have zws between all tokens.
    # Create content string with zws between all tokens for the match.
    zws = "\u200B"  # zero-width space
    lctokens = [parser.get_lowercase(t.token) for t in tokens]
    content = zws + zws.join(lctokens) + zws

    sql = sqltext(
        """
        SELECT WoID, WoTextLC FROM words
        WHERE WoLgID=:language_id and WoTokenCount>1
        """
    )
    sql = sql.bindparams(language_id=language.id)
    reclist = db.session.execute(sql).all()
    # dt.step(f"mwords, loaded {len(reclist)} records")
    woids = [int(p[0]) for p in reclist if f"{zws}{p[1]}{zws}" in content]
    # dt.step("mwords, filtered ids")
    # dt.step("mword ids")

    contained_terms_qry = db.session.query(Term).filter(Term.id.in_(woids))

    # Some term entity relationship objects (tags, parents) could be
    # eagerly loaded using ".options(joinedload(Term.term_tags),
    # joinedload(Term.parents))", but any gains in subsequent usage
    # are offset by the slower query!
    all_terms = terms_matching_tokens_qry.union(contained_terms_qry).all()
    # dt.step("union, exec query")

    return all_terms


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
    # dt = DebugTimer("get_paragraphs", False)

    # Hacky reset of state of ParsedToken state.
    # _Shouldn't_ be needed but doesn't hurt, even if it's lame.
    ParsedToken.reset_counters()

    cleaned = re.sub(r" +", " ", s)
    # dt.step("start get_parsed_tokens")
    tokens = language.get_parsed_tokens(cleaned)
    # dt.step("done get_parsed_tokens")

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
    # dt.step("done token.sort")

    terms = _find_all_terms_in_tokens(tokens, language)
    # dt.step("done _find_all_terms_in_tokens")

    paragraphs = _split_tokens_by_paragraph(tokens)
    # dt.step("done _split_tokens_by_paragraph")

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
    # dt.step("done renderable_paragraphs load")

    _add_status_0_terms(renderable_paragraphs, language)
    # dt.step("done add status 0 terms")

    return renderable_paragraphs
