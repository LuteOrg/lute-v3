"""
Term import.
"""

import os
import tempfile
from flask import Blueprint, render_template, flash, redirect
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms.validators import DataRequired
from lute.termimport.service import import_file, BadImportFileError


bp = Blueprint("termimport", __name__, url_prefix="/termimport")


class TermImportForm(FlaskForm):
    "Form for imports."
    text_file = FileField("Text File", validators=[DataRequired()])


@bp.route("/index", methods=["GET", "POST"])
def term_import_index():
    "Import posted file."
    form = TermImportForm()

    if form.validate_on_submit():
        text_file = form.text_file.data
        if text_file:
            temp_file_name = tempfile.mkstemp()[1]
            try:
                text_file.save(temp_file_name)
                stats = import_file(temp_file_name)
                flash(
                    f"Imported {stats['created']} terms (skipped {stats['skipped']})",
                    "notice",
                )
                return redirect("/term/index", 302)
            except BadImportFileError as e:
                flash(f"Error on import: {str(e)}", "notice")
            finally:
                os.unlink(temp_file_name)

    return render_template("termimport/index.html", form=form)
