"""
Language blueprint.
"""

from flask import Blueprint

bp = Blueprint('language', __name__, url_prefix='/language')

from lute.language import routes
