"""
Reading helpers.
"""

from lute.models.term import Term
from lute.db import db
# from sqlalchemy import or_


from sqlalchemy import func
from sqlalchemy.orm import aliased

def find_all_Terms_in_string(s, language):
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


    # Create an alias for the Term class to use it twice in the query
    term_alias = aliased(Term)
    # Construct content string with zws between all tokens.
    zws = '\u200B'  # zero-width space
    lctokens = [parser.get_lowercase(t.token) for t in tokens]
    content = zws + zws.join(lctokens) + zws
    # Create a query to find terms with multiple tokens that are substrings of the input string
    term_substr_query = db.session.query(term_alias).filter(
        term_alias.language == language,
        term_alias.token_count > 1,
        func.instr(term_alias._text_lc, content) > 0
    )

    terms_matching_substrings = term_substr_query.all()

    # Combine the results from both queries
    result = terms_matching_tokens + terms_matching_substrings
    return result
