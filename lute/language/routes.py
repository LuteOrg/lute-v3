"""
/language endpoints.
"""

from sqlalchemy.exc import IntegrityError
from flask import Blueprint, current_app, render_template, redirect, url_for, flash, jsonify
from lute.models.language import Language
from lute.language.forms import LanguageForm
from lute.db import db

bp = Blueprint('language', __name__, url_prefix='/language')

@bp.route('/index')
def index():
    """
    List all languages.
    """
    languages = Language.query.all()
    return render_template('language/index.html', languages=languages)


def _handle_form(language, form) -> bool:
    """
    Handle the language form processing.

    Returns True if validated and saved.
    """
    result = False

    if form.validate_on_submit():
        try:
            form.populate_obj(language)
            current_app.db.session.add(language)
            current_app.db.session.commit()
            flash(f'Language {language.name} updated', 'success')
            result = True
        except IntegrityError as e:
            # TODO language: better integrity error message - currently shows raw message.
            flash(e.orig.args, 'error')

    return result


@bp.route('/edit/<int:langid>', methods=['GET', 'POST'])
def edit(langid):
    """
    Edit a language.
    """
    language = db.session.get(Language, langid)

    if not language:
        flash(f'Language {langid} not found', 'danger')
        return redirect(url_for('language.index'))

    form = LanguageForm(obj=language)
    if _handle_form(language, form):
        return redirect(url_for('language.index'))
    return render_template('language/edit.html', form=form, language=language)


@bp.route('/new', defaults={'langname': None}, methods=['GET', 'POST'])
@bp.route('/new/<string:langname>', methods=['GET', 'POST'])
def new(langname):
    """
    Create a new language.
    """
    predefined = Language.get_predefined()
    language = Language()
    if langname is not None:
        candidates = [lang for lang in predefined if lang.name == langname]
        if len(candidates) == 1:
            language = candidates[0]

    form = LanguageForm(obj=language)
    if _handle_form(language, form):
        return redirect(url_for('language.index'))

    return render_template('language/new.html', form=form, language=language, predefined=predefined)


# TODO language delete: method for posting


@bp.route('/jsonlist', methods=['GET'], endpoint='app_language_jsonlist')
def jsonlist():
    languages = Language.query.all()  # Assuming Language is your SQLAlchemy model

    language_data = {}
    for language in languages:
        term_dicts = [
            language.dict_1_uri,
            language.dict_2_uri
        ]
        term_dicts = [uri for uri in term_dicts if uri is not None]

        data = {
            'term': term_dicts,
            'sentence': language.sentence_translate_uri
        }

        language_data[language.id] = data

    return jsonify(language_data)
