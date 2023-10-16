"""
Language blueprint.
"""

from flask import Blueprint
from lute.language import routes

bp = Blueprint('language', __name__, url_prefix='/language')
