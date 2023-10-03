"""
/language endpoints.
"""

from flask import Blueprint, render_template, redirect, url_for, flash
from lute.models.language import Language
from lute.forms import LanguageForm
from lute import db

bp = Blueprint('language', __name__, url_prefix='/language')


@bp.route('/index')
def index():
    """
    List all languages.
    """
    languages = Language.query.all()
    return render_template('language/index.html', languages=languages)


@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    """
    Edit a language.
    """
    language = Language.query.get(id)
    if not language:
        flash('Language not found', 'danger')
        return redirect(url_for('language.index'))

    form = LanguageForm(obj=language)

    if form.validate_on_submit():
        form.populate_obj(language)
        db.session.add(language)
        db.session.commit()
        flash('Language updated successfully', 'success')
        return redirect(url_for('language.index'))

    return render_template('language/edit.html', form=form, language=language)
