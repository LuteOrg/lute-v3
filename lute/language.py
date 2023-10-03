"""
/language endpoints.
"""

from sqlalchemy.exc import IntegrityError
from flask import Blueprint, current_app, render_template, redirect, url_for, flash
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
        flash(f'Language {id} not found', 'danger')
        return redirect(url_for('language.index'))

    form = LanguageForm(obj=language)

    if form.validate_on_submit():
        try:
            form.populate_obj(language)
            current_app.db.session.add(language)
            current_app.db.session.commit()
            flash(f'Language {language.name} updated', 'success')
            return redirect(url_for('language.index'))
        except IntegrityError as e:
            # TODO:better_integrity_error - currently shows raw message.
            flash(e.orig.args, 'error')
        except Error as e:
            flash(e, 'error')

    return render_template('language/edit.html', form=form, language=language)


@bp.route('/new', methods=['GET', 'POST'])
def new():
    """
    Create a new language.
    """
    language = Language()
    form = LanguageForm(obj=language)

    if form.validate_on_submit():
        try:
            form.populate_obj(language)
            current_app.db.session.add(language)
            current_app.db.session.commit()
            flash(f'Language {language.name} created', 'success')
            return redirect(url_for('language.index'))
        except IntegrityError as e:
            # TODO:better_integrity_error - currently shows raw message.
            flash(e.orig.args, 'error')
        except Error as e:
            flash(e, 'error')

    return render_template('language/edit.html', form=form, language=language)
