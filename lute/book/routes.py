"""
/book routes.
"""

from flask import Blueprint, request, jsonify, render_template
from lute.utils.data_tables import DataTablesFlaskParamParser
from lute.book.datatables import get_data_tables_list
from lute.book.forms import NewBookForm

# Book domain object
from lute.book.model import Book, Repository


bp = Blueprint('book', __name__, url_prefix='/book')

def datatables_source(is_archived):
    "Get datatables json for books."
    parameters = DataTablesFlaskParamParser.parse_params(request.form)
    data = get_data_tables_list(parameters, is_archived)
    return jsonify(data)


@bp.route('/datatables/active', methods=['POST'])
def datatables_active_source():
    "Datatables data for active books."
    return datatables_source(False)


@bp.route('/datatables/archived', methods=['POST'])
def datatables_archived_source():
    "Datatables data for archived books."
    return datatables_source(True)


@bp.route('/new', methods=['GET', 'POST'])
def new():
    b = Book()
    form = NewBookForm()

    if form.validate_on_submit():
        text_file = request.files['TextFile']
        if text_file:
            content = text_file.read()
            b.Text = content

        book = repo.add(b)
        repo.commit()
        return redirect('/read/{book.id}/page/1')

    return render_template('book/create_new.html', book=b, form=form, showlanguageselector=True)
