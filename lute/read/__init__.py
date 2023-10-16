"""
/read endpoints.
"""

from flask import Blueprint
from lute.read import routes

bp = Blueprint('read', __name__, url_prefix='/read')
