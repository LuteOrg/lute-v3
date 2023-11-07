"""
/termtag routes.
"""

from flask import Blueprint, request, jsonify, render_template, redirect
from lute.models.term import TermTag
from lute.utils.data_tables import DataTablesFlaskParamParser
from lute.termtag.datatables import get_data_tables_list
from lute.db import db
from lute.termtag.forms import TermTagForm

bp = Blueprint("termtag", __name__, url_prefix="/termtag")


@bp.route("/index", defaults={"search": None}, methods=["GET"])
@bp.route("/index/<search>", methods=["GET"])
def index(search):
    "Index page."
    return render_template("termtag/index.html", initial_search=search)


@bp.route("/datatables", methods=["POST"])
def datatables_active_source():
    "Datatables data for terms."
    parameters = DataTablesFlaskParamParser.parse_params(request.form)
    data = get_data_tables_list(parameters)
    return jsonify(data)


def _handle_form(termtag, form_template_name):
    """
    Handle a form post.
    """
    form = TermTagForm(obj=termtag)

    if form.validate_on_submit():
        form.populate_obj(termtag)
        db.session.add(termtag)
        db.session.commit()
        return redirect("/termtag/index", 302)

    return render_template(form_template_name, form=form, termtag=termtag)


@bp.route("/edit/<int:termtagid>", methods=["GET", "POST"])
def edit(termtagid):
    """
    Edit a termtag
    """
    termtag = TermTag.find(termtagid)
    return _handle_form(termtag, "termtag/edit.html")


@bp.route("/new", methods=["GET", "POST"])
def new():
    """
    Create a termtag.
    """
    tt = TermTag("")
    return _handle_form(tt, "termtag/new.html")


@bp.route("/delete/<int:termtagid>", methods=["POST"])
def delete(termtagid):
    """
    Delete a termtag.
    """
    termtag = TermTag.find(termtagid)
    db.session.delete(termtag)
    db.session.commit()
    return redirect("/termtag/index", 302)
