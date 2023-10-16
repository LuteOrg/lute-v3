"""
/read endpoints.
"""

from flask import Blueprint

bp = Blueprint('read', __name__, url_prefix='/read')

from lute.read import routes
