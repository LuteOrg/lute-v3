"""
/read endpoints.
"""

from flask import request, jsonify
from lute.utils.data_tables import DataTablesFlaskParamParser
from lute.models.book import Book

from . import bp

@bp.route('/<int:bookid>/page/<int:pagenum>', methods=['GET'])
def read(bookid, pagenum):
    "Display reading pane for book page."
    return f"TODO book: reading book {bookid} page {pagenum}"
