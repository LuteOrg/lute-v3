"""
Mapping parents.
"""

# TODO issue_336_export_unknown_book_terms: this blueprint can be killed when 336 is done.

import os
from flask import Blueprint, current_app, render_template, send_file
from sqlalchemy import asc
from lute.db import db
from lute.models.book import Book
from lute.models.language import Language
from lute.term_parent_map.service import export_unknown_terms


bp = Blueprint("term_parent_map", __name__, url_prefix="/term_parent_map")


@bp.route("/index", methods=["GET", "POST"])
def index():
    """
    Show books and languages
    """

    # sqlalchemy _requires_ "== False" for the comparison!
    # pylint: disable=singleton-comparison
    books = (
        db.session.query(Book)
        .filter(Book.archived == False)
        .order_by(asc(Book.title))
        .all()
    )
    languages = db.session.query(Language).order_by(asc(Language.name)).all()
    return render_template(
        "/term_parent_map/index.html", books=books, languages=languages
    )


# TODO issue_336_export_unknown_book_terms: move this route, or something like it, to book actions.
@bp.route("/export_book/<int:bookid>", methods=["GET"])
def export_book(bookid):
    "Generate a file and return it."
    outfile = os.path.join(current_app.env_config.temppath, "export_book.txt")
    book = db.session.get(Book, bookid)
    export_unknown_terms(book, outfile)
    return send_file(outfile, as_attachment=True, download_name="unknown_terms.txt")
