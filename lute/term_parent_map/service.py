"""
Term parent mapping.
"""

from lute.db import db
from lute.models.term import Term


## Exports


# TODO issue_336_export_unknown_book_terms: move this where needed.
def export_unknown_terms(book, outfile):
    "Export unknown terms in the book to outfile."
    lang = book.language
    unique_tokens = {
        t for txt in book.texts for t in lang.get_parsed_tokens(txt.text) if t.is_word
    }
    unique_lcase_toks = {lang.get_lowercase(t.token) for t in unique_tokens}

    lgid = lang.id
    known_terms_lc = (
        db.session.query(Term.text_lc)
        .filter(Term.language_id == lgid, Term.token_count == 1)
        .all()
    )
    known_terms_lc = [word[0] for word in known_terms_lc]

    newtoks = [t for t in unique_lcase_toks if t not in known_terms_lc]
    with open(outfile, "w", encoding="utf-8") as f:
        f.write("\n".join(newtoks))
