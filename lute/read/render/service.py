"""
Reading rendering helpers.
"""

import itertools
import re
from sqlalchemy import text as sqltext

from lute.models.term import Term
from lute.parse.base import ParsedToken
from lute.read.render.calculate_textitems import get_textitems
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


# TODO cache_multiword_terms.
#
# Caching all multiword terms cuts down stats calculation time.
# e.g. when calculating stats on 100 pages, the time goes from 0.7s to 0.01s.
#
# Have to sort out cache invalidation (esp for unit tests), and
# separate caches for each language.
# _cached_multiword_terms = None


def _get_multiword_terms(language):
    "Get all multiword terms."

    # TODO cache_multiword_terms.
    # global _cached_multiword_terms
    # if _cached_multiword_terms is not None:
    #    return _cached_multiword_terms

    sql = sqltext(
        """
        SELECT WoID, WoTextLC FROM words
        WHERE WoLgID=:language_id and WoTokenCount>1
        """
    )
    sql = sql.bindparams(language_id=language.id)
    _cached_multiword_terms = db.session.execute(sql).all()
    return _cached_multiword_terms


def _find_all_terms_in_tokens(tokens, language):
    """
    Find all terms contained in the (ordered) parsed tokens tokens.

    For example
    - given tokens = "Here", " ", "is", " ", "a", " ", "cat"
    - given terms in the db: [ "cat", "a/ /cat", "dog" ]

    This would return the terms "cat" and "a/ /cat".

    Method:
    - build list of lowercase text in the tokens
    - append all multword term strings that exist in the content
    - query for Terms that exist in the list
    """

    # Performance breakdown:
    #
    # About half of the time is spent in "performance hit 1",
    # filtering the multiword terms to find those contained in the
    # text.  A bit less than half is spent is "performance hit 2", the
    # actual query.
    #
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

    # dt = DebugTimer("_find_all_terms_in_tokens", display=False)

    parser = language.parser

    # Each token can map to a single-word Term.
    text_lcs = [parser.get_lowercase(t.token) for t in tokens]

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
    # Note that querying using 'LIKE' is also slow, i.e:
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
    reclist = _get_multiword_terms(language)
    # dt.step(f"mwords, loaded {len(reclist)} records")

    # Performance hit 1
    zws = "\u200B"  # zero-width space
    content = zws + zws.join(text_lcs) + zws
    mword_terms = [p[1] for p in reclist if f"{zws}{p[1]}{zws}" in content]
    # dt.step("mword terms")
    text_lcs.extend(mword_terms)

    # Some term entity relationship objects (tags, parents) could be
    # eagerly loaded using ".options(joinedload(Term.term_tags),
    # joinedload(Term.parents))", but any gains in subsequent usage
    # are offset by the slower query!
    # Performance hit 2
    tok_strings = list(set(text_lcs))
    terms_matching_tokens_qry = db.session.query(Term).filter(
        Term.text_lc.in_(tok_strings), Term.language == language
    )
    # dt.step("query prep")

    all_terms = terms_matching_tokens_qry.all()
    # dt.step("exec query")

    return all_terms


## Getting paragraphs ##############################


def get_paragraphs(s, language):
    """
    Get array of arrays of TextItems for the given string s.
    """
    # dt = DebugTimer("get_paragraphs", display=False)

    # Hacky reset of state of ParsedToken state.
    # _Shouldn't_ be needed but doesn't hurt, even if it's lame.
    ParsedToken.reset_counters()

    cleaned = re.sub(r" +", " ", s)
    tokens = language.get_parsed_tokens(cleaned)
    # dt.step("get_parsed_tokens")

    terms = _find_all_terms_in_tokens(tokens, language)

    textitems = get_textitems(tokens, terms, language)

    def _split_textitems_by_paragraph(textitems):
        "Split by ¶"
        ret = []
        curr_para = []
        for t in textitems:
            if t.text == "¶":
                ret.append(curr_para)
                curr_para = []
            else:
                curr_para.append(t)
        if len(curr_para) > 0:
            ret.append(curr_para)
        return ret

    def _split_by_sentence_number(p):
        return [
            list(sentence)
            for _, sentence in itertools.groupby(p, key=lambda t: t.sentence_number)
        ]

    paras = [
        _split_by_sentence_number(list(sentences))
        for sentences in _split_textitems_by_paragraph(textitems)
    ]

    return paras
