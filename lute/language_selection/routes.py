"""
Routes for language selection (i18n).
"""

from flask import Blueprint, session, redirect, request, current_app

bp = Blueprint("language_selection", __name__, url_prefix="/language")

@bp.route("/set/<language>")
def set_language(language=None):
    """Set the user's preferred language."""
    languages = current_app.config.get('LANGUAGES', {})
    if language and language in languages.keys():
        session['language'] = language
    
    # Redirect to the page the user came from, or to the home page
    return redirect(request.referrer or '/')