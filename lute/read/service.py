"""
Reading helpers.
"""

import re
from sqlalchemy import func

from lute.models.term import Term
from lute.db import db


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
    cleaned = re.sub(r'\s+', ' ', s)
    tokens = language.get_parsed_tokens(cleaned)

    parser = language.parser

    # Query for terms with a single token that match the unique word tokens
    word_tokens = filter(lambda t: t.is_word, tokens)
    tok_strings = [parser.get_lowercase(t.token) for t in word_tokens]
    tok_strings = list(set(tok_strings))
    terms_matching_tokens = db.session.query(Term).filter(
        Term.language == language,
        Term.text_lc.in_(tok_strings),
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
        func.instr(content, Term.text_lc) > 0
    )
    contained_terms = contained_term_query.all()

    return terms_matching_tokens + contained_terms


class RenderableSentence:
    """
    A collection of TextItems to be rendered.
    """
    def __init__(self, sentence_id, textitems):
        self.SeID = sentence_id
        self.textitems = textitems


def get_paragraphs(text, svc):
    if text.getID() is None:
        return []

    tokens = getTextTokens(text)
    tokens = [t for t in tokens if t.TokText != '¶']

    language = text.getBook().getLanguage()
    terms = svc.findAllInString(text.text, language)

    def makeRenderableSentence(pnum, sentence_num, tokens, terms, text, language):
        setokens = [t for t in tokens if t.TokSentenceNumber == sentence_num]
        renderable = RenderableCalculator.getRenderable(language, terms, setokens)
        textitems = [
            i.makeTextItem(pnum, sentence_num, text.getID(), language)
            for i in renderable
        ]
        return RenderableSentence(sentence_num, textitems)

    paranums = [t.TokParagraphNumber for t in tokens]
    paranums = list(set(paranums))
    renderableParas = []

    for pnum in paranums:
        paratokens = [t for t in tokens if t.TokParagraphNumber == pnum]
        senums = [t.TokSentenceNumber for t in paratokens]
        senums = list(set(senums))
        renderableParas.append(
            [makeRenderableSentence(pnum, senum, paratokens, terms, text, language) for senum in senums]
        )

    return renderableParas

def getTextTokens(t):
    text_id = t.getID()
    if text_id is None:
        return []
    pts = t.getBook().getLanguage().getParsedTokens(t.text)
    return ParsedToken.createTextTokens(pts)
