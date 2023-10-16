"""
/book blueprint.
"""

from flask import Blueprint
from lute.book import routes

bp = Blueprint('book', __name__, url_prefix='/book')
