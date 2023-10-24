"""
/term routes.
"""

from flask import Blueprint, request, jsonify, render_template
from lute.utils.data_tables import DataTablesFlaskParamParser
from lute.term.datatables import get_data_tables_list

bp = Blueprint('term', __name__, url_prefix='/term')

@bp.route('/index', defaults={'search': None}, methods=['GET'])
@bp.route('/index/<search>', methods=['GET'])
def index(search):
    "Index page."
    return render_template(
        'term/index.html',
        initial_search = search
    )

@bp.route('/datatables', methods=['POST'])
def datatables_active_source():
    "Datatables data for terms."
    parameters = DataTablesFlaskParamParser.parse_params(request.form)

    # The DataTablesFlaskParamParser doesn't know about term-specific filters,
    # add those manually.
    filter_param_names = [
        'filtParentsOnly',
        'filtAgeMin',
        'filtAgeMax',
        'filtStatusMin',
        'filtStatusMax',
        'filtIncludeIgnored'
    ]
    request_params = request.form.to_dict(flat=True)
    for p in filter_param_names:
        parameters[p] = request_params.get(p)

    data = get_data_tables_list(parameters)
    return jsonify(data)
