"""
Mapping parents.
"""

import os
import tempfile
from flask import Blueprint, render_template, flash, redirect, send_file
from wtforms import SelectField, ValidationError
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from sqlalchemy import asc
from lute.db import db
from lute.models.book import Book
from lute.models.language import Language
import lute.utils.formutils
from lute.term_parent_map.service import (
    import_file,
    BadImportFileError,
    export_unknown_terms,
    export_terms_without_parents,
)


bp = Blueprint("term_parent_map", __name__, url_prefix="/term_parent_map")


class TermParentMapImportForm(FlaskForm):
    "Form for imports."
    language_id = SelectField("Language", coerce=int)
    text_file = FileField("Text File", validators=[DataRequired()])

    def validate_language_id(self, field):  # pylint: disable=unused-argument
        "Language must be set."
        if self.language_id.data in (None, 0):
            raise ValidationError("Please select a language")


@bp.route("/index", methods=["GET", "POST"])
def index():
    """
    Show books and languages, process import post.
    """
    form = TermParentMapImportForm()
    form.language_id.choices = lute.utils.formutils.language_choices()

    if form.validate_on_submit():
        text_file = form.text_file.data
        language = db.session.get(Language, form.language_id.data)
        if text_file:
            temp_file_name = tempfile.mkstemp()[1]
            try:
                text_file.save(temp_file_name)
                stats = import_file(language, temp_file_name)
                msg = (
                    f"Imported {language.name} mappings: "
                    + f"created {stats['created']} terms, updated {stats['updated']}."
                )
                flash(msg, "notice")
                return redirect("/term_parent_map/index", 302)
            except BadImportFileError as e:
                flash(f"Error on import: {str(e)}", "notice")
            finally:
                os.unlink(temp_file_name)

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
        "/term_parent_map/index.html", books=books, languages=languages, form=form
    )


@bp.route("/export_book/<int:bookid>", methods=["GET"])
def export_book(bookid):
    "Generate a file and return it."
    temp_file_name = tempfile.mkstemp()[1]
    book = db.session.get(Book, bookid)
    export_unknown_terms(book, temp_file_name)
    return send_file(
        temp_file_name, as_attachment=True, download_name="unknown_terms.txt"
    )


@bp.route("/export_language/<int:languageid>", methods=["GET"])
def export_language(languageid):
    "Generate a file and return it."
    temp_file_name = tempfile.mkstemp()[1]
    lang = db.session.get(Language, languageid)
    export_terms_without_parents(lang, temp_file_name)
    return send_file(
        temp_file_name, as_attachment=True, download_name="terms_without_parents.txt"
    )
