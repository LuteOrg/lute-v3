"""
/language endpoints.
"""

from flask import Blueprint, render_template

from lute.models.language import Language

bp = Blueprint('language', __name__, url_prefix='/language')

@bp.route('/index')
def index():
    """
    List all languages.
    """
    languages = Language.query.all()
    return render_template('language/index.html', languages=languages)
