"""
/language endpoints.
"""

from flask import Blueprint, render_template

from lute.db import db
from lute.models.language import Language

bp = Blueprint('language', __name__, url_prefix='/language')

@bp.route('/index')
def index():
    """
    List all languages.
    """
    languages = db.session.execute(db.select(Language).order_by(Language.name)).scalars()
    return render_template('language/index.html', languages=languages)
