"""
/book blueprint.
"""

from flask import Blueprint

bp = Blueprint('book', __name__, url_prefix='/book')

from lute.book import routes
