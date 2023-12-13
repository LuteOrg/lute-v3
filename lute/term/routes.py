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
import lute.utils.formutils

bp = Blueprint("term", __name__, url_prefix="/term")


@bp.route("/index", defaults={"search": None}, methods=["GET"])
@bp.route("/index/<search>", methods=["GET"])
def index(search):
    "Index page."
    languages = db.session.query(Language).order_by(Language.name).all()
    langopts = [(lang.id, lang.name) for lang in languages]
    langopts = [(0, "(all)")] + langopts
    return render_template(
        "term/index.html", initial_search=search, language_options=langopts
    )


@bp.route("/datatables", methods=["POST"])
def datatables_active_source():
    "Datatables data for terms."
    parameters = DataTablesFlaskParamParser.parse_params(request.form)

    # The DataTablesFlaskParamParser doesn't know about term-specific filters,
    # add those manually.
    filter_param_names = [
        "filtLanguage",
        "filtParentsOnly",
        "filtAgeMin",
        "filtAgeMax",
        "filtStatusMin",
        "filtStatusMax",
        "filtIncludeIgnored",
    ]
    request_params = request.form.to_dict(flat=True)
    for p in filter_param_names:
        parameters[p] = request_params.get(p)

    data = get_data_tables_list(parameters)
    return jsonify(data)


def handle_term_form(
    term, repo, form_template_name, return_on_success, embedded_in_reading_frame=False
):
    """
    Handle a form post.

    This is used here and in read.routes -- read.routes.term_form
    lives in an iframe in the reading frames and returns a different
    template on success.
    """
    form = TermForm(obj=term)

    # Flash messages get added on things like term imports.
    # The user opening the form is treated as an acknowledgement.
    term.flash_message = None

    form.language_id.choices = lute.utils.formutils.language_choices()

    if form.validate_on_submit():
        form.populate_obj(term)
        repo.add(term)
        repo.commit()
        return return_on_success

    hide_pronunciation = False
    # pylint: disable=protected-access
    if term._language is not None:
        hide_pronunciation = not term._language.show_romanization

    return render_template(
        form_template_name,
        form=form,
        term=term,
        language_dicts=Language.all_dictionaries(),
        hide_pronunciation=hide_pronunciation,
        tags=repo.get_term_tags(),
        embedded_in_reading_frame=embedded_in_reading_frame,
    )


def _handle_form(term, repo):
    """
    Handle the form post.  Only show lang. selector
    for new terms.
    """
    return handle_term_form(
        term, repo, "/term/formframes.html", redirect("/term/index", 302)
    )


@bp.route("/edit/<int:termid>", methods=["GET", "POST"])
def edit(termid):
    """
    Edit a term.
    """
    repo = Repository(db)
    term = repo.load(termid)
    return _handle_form(term, repo)


@bp.route("/editbytext/<int:langid>/<text>", methods=["GET", "POST"])
def edit_by_text(langid, text):
    """
    Edit a term.
    """
    repo = Repository(db)
    term = repo.find_or_new(langid, text)
    return _handle_form(term, repo)


@bp.route("/new", methods=["GET", "POST"])
def new():
    """
    Create a term.
    """
    repo = Repository(db)
    term = Term()
    return _handle_form(term, repo)


@bp.route("/search/<text>/<int:langid>", methods=["GET"])
def search_by_text_in_language(text, langid):
    "JSON data for parent data."
    if text.strip() == "" or langid == 0:
        return []
    repo = Repository(db)
    matches = repo.find_matches(langid, text)
    result = []
    for t in matches:
        result.append({"id": t.id, "text": t.text, "translation": t.translation})
    return jsonify(result)


@bp.route("/sentences/<int:langid>/<text>", methods=["GET"])
def sentences(langid, text):
    "Get sentences for terms."
    repo = Repository(db)
    # Use find_or_new(): if the user clicks on a parent tag
    # in the term form, and the parent does not exist yet, then
    # we're creating a new term.
    t = repo.find_or_new(langid, text)
    refs = repo.find_references(t)

    # Transform data for output, to
    # { "term": [refs], "children": [refs], "parent1": [refs], "parent2" ... }
    refdata = [(f'"{text}"', refs["term"]), (f'"{text}" child terms', refs["children"])]
    for p in refs["parents"]:
        refdata.append((f"\"{p['term']}\"", p["refs"]))

    refcount = sum(len(ref[1]) for ref in refdata)
    return render_template(
        "/term/sentences.html",
        text=text,
        no_references=(refcount == 0),
        references=refdata,
    )


@bp.route("/bulk_update_status", methods=["POST"])
def bulk_update_status():
    "Update the statuses."
    data = request.get_json()
    terms = data.get("terms")
    language_id = int(data.get("langid"))
    new_status = int(data.get("new_status"))

    repo = Repository(db)
    for t in terms:
        term = repo.find_or_new(language_id, t)
        term.status = new_status
        repo.add(term)
    repo.commit()
    return jsonify("ok")


@bp.route("/bulk_set_parent", methods=["POST"])
def bulk_set_parent():
    "Set the parent for terms."
    data = request.get_json()
    termids = data.get("wordids")
    parenttext = data.get("parenttext")
    repo = Repository(db)
    for tid in termids:
        term = repo.load(int(tid))
        term.parents = [parenttext]
        repo.add(term)
    repo.commit()
    return jsonify("ok")


@bp.route("/delete/<int:termid>", methods=["POST"])
def delete(termid):
    """
    Delete a term.
    """
    repo = Repository(db)
    term = repo.load(termid)
    repo.delete(term)
    repo.commit()
    return redirect("/term/index", 302)
