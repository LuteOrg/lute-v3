"""
/book routes.
"""

from flask import Blueprint, request, jsonify, render_template, redirect, flash
from lute.utils.data_tables import DataTablesFlaskParamParser
from lute.book.datatables import get_data_tables_list
from lute.book.forms import NewBookForm, EditBookForm
import lute.utils.formutils
from lute.db import db

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
    "Create a new book, either from text or from a file."
    b = Book()
    form = NewBookForm(obj=b)
    form.language_id.choices = lute.utils.formutils.language_choices()
    repo = Repository(db)

    if form.validate_on_submit():
        form.populate_obj(b)
        if form.textfile.data:
            content = form.textfile.data.read()
            b.text = str(content, 'utf-8')
        book = repo.add(b)
        repo.commit()
        return redirect(f'/read/{book.id}/page/1', 302)

    return render_template(
        'book/create_new.html',
        book=b,
        form=form,
        tags = repo.get_book_tags(),
        show_language_selector=True
    )


@bp.route('/edit/<int:bookid>', methods=['GET', 'POST'])
def edit(bookid):
    "Edit a book - can only change a few fields."
    repo = Repository(db)
    b = repo.load(bookid)
    form = EditBookForm(obj=b)

    if form.validate_on_submit():
        form.populate_obj(b)
        repo.add(b)
        repo.commit()
        flash(f'{b.title} updated.')
        return redirect('/', 302)

    return render_template(
        'book/edit.html',
        book=b,
        form=form,
        tags = repo.get_book_tags()
    )
