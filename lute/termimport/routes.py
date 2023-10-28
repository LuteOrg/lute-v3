"""
Term import.
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, Response
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename
from lute.termimport.service import import_file, BadImportFileError


bp = Blueprint('termimport', __name__, url_prefix='/termimport')


class TermImportForm(FlaskForm):
    "Form for imports."
    text_file = FileField('Text File')


@bp.route('/index', methods=['GET', 'POST'])
def term_import_index():
    form = TermImportForm()

    if form.validate_on_submit():
        text_file = form.text_file.data
        if text_file:
            try:
                filename = secure_filename(text_file.filename)
                text_file.save(filename)
                stats = import_file(filename)
                flash(f"Imported {stats['created']} terms (skipped {stats['skipped']})", 'notice')
                return redirect('/term/index', 302)
            except BadImportFileError as e:
                flash(f"Error on import: {str(e)}", 'notice')

    return render_template('termimport/index.html', form=form)
