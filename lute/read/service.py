"""
Reading helpers.
"""

from lute.models.term import Term
from lute.db import db
# from sqlalchemy import or_


from sqlalchemy import func
from sqlalchemy.orm import aliased

def find_all_Terms_in_string(s, language):
    """
    Find all terms contained in the string s.

    For example
    - given s = "Here is a cat"
    - given terms in the db: [ "cat", "a cat", "dog" ]

    This would return the terms "cat" and "a cat".

    The code first queries for exact single-token matches,
    and then multiword matches, because that's much faster
    than querying for everthing at once.  (This may no longer
    be true, can change it later.)
    """

    # Extract word tokens from the input string
    tokens = language.get_parsed_tokens(s)

    parser = language.parser

    # Query for terms with a single token that match the unique word tokens
    word_tokens = filter(lambda t: t.is_word, tokens)
    tok_strings = [parser.get_lowercase(t.token) for t in word_tokens]
    tok_strings = list(set(tok_strings))
    terms_matching_tokens = db.session.query(Term).filter(
        Term.language == language,
        Term._text_lc.in_(tok_strings),
        Term.token_count == 1
    ).all()

    # Multiword terms have zws between all tokens.
    # Create content string with zws between all tokens for the match.
    zws = '\u200B'  # zero-width space
    lctokens = [parser.get_lowercase(t.token) for t in tokens]
    content = zws + zws.join(lctokens) + zws
    contained_term_query = db.session.query(Term).filter(
        Term.language == language,
        Term.token_count > 1,
        func.instr(content, Term._text_lc) > 0
    )
    contained_terms = contained_term_query.all()

    return terms_matching_tokens + contained_terms
