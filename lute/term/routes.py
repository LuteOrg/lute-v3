"""
/term routes.
"""

from flask import Blueprint, request, jsonify, render_template, redirect
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


def _handle_form(term, form) -> bool:
    """
    Handle the read term form processing.
    Returns True if validated and saved.
    """
    if not form.validate_on_submit():
        return False

    form.populate_obj(term)
    if term.text_has_changed():
        flash('Can only change term case.', 'error')
        term.text = term.original_text
        form = TermForm(obj=term)
        return False

    ret = False
    try:
        repo = Repository(db)
        repo.add(term)
        repo.commit()

        # Don't add a flash message here.  When the reading term is
        # updated, it shows the read/updated.html template, which has
        # its own "flash" message.  Adding a flash here would send the
        # message to the base.html template.
        # flash(f'Term {term.text} updated', 'success')
        ret = True

    except IntegrityError as e:
        # TODO term: better integrity error message - currently
        # shows raw message.
        # TODO check if used: not sure if this will ever occur
        flash(e.orig.args, 'error')

    return ret


@bp.route('/edit/<int:termid>', methods=['GET', 'POST'])
def edit(termid):
    """
    Edit a term.
    """
    repo = Repository(db)
    term = repo.load(termid)

    form = TermForm(obj=term)
    resp = _handle_form(term, form)
    if resp is True:
        return redirect('/', 302)

    return render_template(
        '/term/formframes.html',
        form=form,
        term=term,
        newterm = False,
        language_dicts=Language.all_dictionaries(),
    )


@bp.route('/new', methods=['GET', 'POST'])
def new():
    """
    Create a term.
    """
    repo = Repository(db)
    term = Term()
    form = TermForm(obj=term)
    resp = _handle_form(term, form)
    if resp is True:
        return redirect('/', 302)

    return render_template(
        '/term/formframes.html',
        form=form,
        term=term,
        newterm = True,
        language_dicts=Language.all_dictionaries(),
    )
