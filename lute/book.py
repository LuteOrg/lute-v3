"""
/book endpoints.
"""

from flask import Blueprint, request, jsonify
from lute.utils.data_tables import DataTablesFlaskParamParser
from lute.models.book import Book

bp = Blueprint('book', __name__, url_prefix='/book')

def datatables_source(is_archived):
    "Get datatables json for books."
    parameters = DataTablesFlaskParamParser.parse_params(request.form)
    data = Book.get_data_tables_list(parameters, is_archived)
    return jsonify(data)


@bp.route('/datatables/active', methods=['POST'])
def datatables_active_source():
    "Datatables data for active books."
    return datatables_source(False)


@bp.route('/datatables/archived', methods=['POST'])
def datatables_archived_source():
    "Datatables data for archived books."
    return datatables_source(True)


@bp.route('/read/<int:bookid>', methods=['GET'])
def read(bookid):
    "Display reading pane for book with given id."
    return f"TODO book: reading book {bookid}"
