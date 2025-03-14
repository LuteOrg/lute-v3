"""
Term import.
"""

import os
from flask import Blueprint, current_app, render_template, flash, redirect
from wtforms import BooleanField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from lute.termimport.service import Service, BadImportFileError
from lute.db import db


bp = Blueprint("termimport", __name__, url_prefix="/termimport")


class TermImportForm(FlaskForm):
    "Form for imports."
    text_file = FileField("Text File", validators=[DataRequired()])
    create_terms = BooleanField("Create new terms")
    new_as_unknown = BooleanField("Set new terms to Unknown")
    update_terms = BooleanField("Update existing terms")


@bp.route("/index", methods=["GET", "POST"])
def term_import_index():
    "Import posted file."
    form = TermImportForm()
    service = Service(db.session)
    if form.validate_on_submit():
        text_file = form.text_file.data
        if text_file:
            temp_file_name = os.path.join(
                current_app.env_config.temppath, "import_terms.txt"
            )
            text_file.save(temp_file_name)
            try:
                stats = service.import_file(
                    temp_file_name,
                    form.create_terms.data,
                    form.update_terms.data,
                    form.new_as_unknown.data,
                )
                c = stats["created"]
                u = stats["updated"]
                s = stats["skipped"]
                flash(
                    f"Imported {c} terms, updated {u} (skipped {s})",
                    "notice",
                )
                return redirect("/term/index", 302)
            except BadImportFileError as e:
                flash(f"Error on import: {str(e)}", "notice")

    return render_template("termimport/index.html", form=form)
