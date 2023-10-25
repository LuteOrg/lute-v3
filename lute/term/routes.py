"""
/term routes.
"""

from flask import Blueprint, request, jsonify, render_template, redirect, flash
from lute.models.language import Language
from lute.utils.data_tables import DataTablesFlaskParamParser
from lute.term.datatables import get_data_tables_list
from lute.term.model import Repository, Term
from lute.db import db
from lute.term.forms import TermForm

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


def _handle_form(term, repo, showlanguageselector):
    """
    Handle the form post.  Only show lang. selector
    for new terms.
    """
    form = TermForm(obj=term)
    if form.validate_on_submit():
        form.populate_obj(term)
        repo.add(term)
        repo.commit()
        return redirect('/term/index', 302)

    return render_template(
        '/term/formframes.html',
        form=form,
        term=term,
        language_dicts=Language.all_dictionaries(),
        showlanguageselector=showlanguageselector,

        # TODO term tags: pass dynamic list.
        tags=[ "apple", "bear", "cat" ],
        parent_link_to_frame=True
    )


@bp.route('/edit/<int:termid>', methods=['GET', 'POST'])
def edit(termid):
    """
    Edit a term.
    """
    repo = Repository(db)
    term = repo.load(termid)
    return _handle_form(term, repo, False)


@bp.route('/new', methods=['GET', 'POST'])
def new():
    """
    Create a term.
    """
    repo = Repository(db)
    term = Term()
    return _handle_form(term, repo, True)
