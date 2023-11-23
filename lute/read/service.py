"""
Reading helpers.
"""

import re
from sqlalchemy import func

from lute.models.term import Term, Status
from lute.models.book import Text
from lute.parse.base import ParsedToken
from lute.read.render.renderable_calculator import RenderableCalculator
from lute.term.model import Repository

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
    cleaned = re.sub(r"\s+", " ", s)
    tokens = language.get_parsed_tokens(cleaned)

    parser = language.parser

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
    contained_term_query = db.session.query(Term).filter(
        Term.language == language,
        Term.token_count > 1,
        func.instr(content, Term.text_lc) > 0,
    )
    contained_terms = contained_term_query.all()

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


def get_paragraphs(text):
    """
    Get array of arrays of RenderableSentences for the given Text.
    """
    if text.id is None:
        return []

    language = text.book.language

    # Hacky reset of state of ParsedToken state.
    # _Shouldn't_ matter ... :-(
    ParsedToken.reset_counters()
    tokens = language.get_parsed_tokens(text.text)
    tokens = [t for t in tokens if t.token != "¶"]

    terms = find_all_Terms_in_string(text.text, language)

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
        textitems = [
            i.make_text_item(pnum, sentence_num, text.id, language) for i in renderable
        ]
        return RenderableSentence(sentence_num, textitems)

    def unique(arr):
        return list(set(arr))

    renderable_paragraphs = []
    paranums = sorted(unique([t.paragraph_number for t in tokens]))
    for pnum in paranums:
        paratokens = [t for t in tokens if t.paragraph_number == pnum]
        senums = sorted(unique([t.sentence_number for t in paratokens]))

        # A renderable paragraph is a collection of
        # RenderableSentences.
        renderable_sentences = [
            make_RenderableSentence(pnum, senum, paratokens, terms) for senum in senums
        ]
        renderable_paragraphs.append(renderable_sentences)

    return renderable_paragraphs


def set_unknowns_to_known(text: Text):
    """
    Given a text, create new Terms with status Well-Known
    for any new Terms.
    """
    language = text.book.language

    sentences = sum(get_paragraphs(text), [])

    tis = []
    for sentence in sentences:
        for ti in sentence.textitems:
            tis.append(ti)

    def is_unknown(ti):
        return (
            ti.is_word == 1
            and (ti.wo_id == 0 or ti.wo_id is None)
            and ti.token_count == 1
        )

    unknowns = list(filter(is_unknown, tis))
    words_lc = [ti.text_lc for ti in unknowns]
    uniques = list(set(words_lc))
    uniques.sort()

    batch_size = 100
    i = 0

    # There is likely a better way to write this using generators and
    # yield.
    for u in uniques:
        candidate = Term(language, u)
        t = Term.find_by_spec(candidate)
        if t is None:
            candidate.status = Status.WELLKNOWN
            db.session.add(candidate)
            i += 1

        if i % batch_size == 0:
            db.session.commit()

    # Commit any remaining.
    db.session.commit()


def bulk_status_update(text: Text, terms_text_array, new_status):
    """
    Given a text and list of terms, update or create new terms
    and set the status.
    """
    language = text.book.language
    repo = Repository(db)
    for term_text in terms_text_array:
        t = repo.find_or_new(language.id, term_text)
        t.status = new_status
        repo.add(t)
    repo.commit()
