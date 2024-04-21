"""
/term routes.
"""

import os
import csv
from flask import (
    Blueprint,
    request,
    jsonify,
    render_template,
    redirect,
    current_app,
    send_file,
)
from lute.models.language import Language
from lute.models.term import Term as DBTerm
from lute.models.setting import UserSetting
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
    DBTerm.delete_empty_images()
    languages = db.session.query(Language).order_by(Language.name).all()
    langopts = [(lang.id, lang.name) for lang in languages]
    langopts = [(0, "(all)")] + langopts
    return render_template(
        "term/index.html", initial_search=search, language_options=langopts
    )


def _load_term_custom_filters(request_form, parameters):
    "Manually add filters that the DataTablesFlaskParamParser doesn't know about."
    filter_param_names = [
        "filtLanguage",
        "filtParentsOnly",
        "filtAgeMin",
        "filtAgeMax",
        "filtStatusMin",
        "filtStatusMax",
        "filtIncludeIgnored",
    ]
    request_params = request_form.to_dict(flat=True)
    for p in filter_param_names:
        parameters[p] = request_params.get(p)


@bp.route("/datatables", methods=["POST"])
def datatables_active_source():
    "Datatables data for terms."
    parameters = DataTablesFlaskParamParser.parse_params(request.form)
    _load_term_custom_filters(request.form, parameters)
    data = get_data_tables_list(parameters)
    return jsonify(data)


@bp.route("/export_terms", methods=["POST"])
def export_terms():
    "Generate export file of terms."
    parameters = DataTablesFlaskParamParser.parse_params(request.form)
    _load_term_custom_filters(request.form, parameters)
    parameters["length"] = 1000000
    outfile = os.path.join(current_app.env_config.temppath, "export_terms.csv")
    data = get_data_tables_list(parameters)
    render_data = data["data"]

    # Fields as returned from the datatables query.
    headings = [
        "OMIT_Checkbox",
        "term",
        "parent",
        "translation",
        "language",
        "tags",
        "OMIT_status_text",
        "added",
        "OMIT_WoID",
        "OMIT_LgID",
        "OMIT_ImageSource",
        "status",
        "link_status",
        "OMIT_status_text",
        "pronunciation",
    ]
    columns_to_exclude = []
    for i, h in enumerate(headings):
        if h.startswith("OMIT_"):
            columns_to_exclude.append(i)

    output_data = [headings] + render_data
    with open(outfile, "w", encoding="utf-8", newline="") as f:
        csv_writer = csv.writer(f)
        for row in output_data:
            filtered_row = [
                value for i, value in enumerate(row) if i not in columns_to_exclude
            ]
            csv_writer.writerow(filtered_row)

    return send_file(outfile, as_attachment=True, download_name="Terms.csv")


def handle_term_form(
    term, repo, form_template_name, return_on_success, embedded_in_reading_frame=False
):
    """
    Handle a form post.

    This is used here and in read.routes -- read.routes.term_form
    lives in an iframe in the reading frames and returns a different
    template on success.
    """
    # print(f"in handle_term_form with term.id = {term.id}", flush=True)
    form = TermForm(obj=term)
    # parents = [{"value": p} for p in term.parents]
    # form.parentslist.data = json.dumps(parents)

    # Flash messages get added on things like term imports.
    # The user opening the form is treated as an acknowledgement.
    term.flash_message = None

    form.language_id.choices = lute.utils.formutils.language_choices()

    if form.validate_on_submit():
        form.populate_obj(term)
        repo.add(term)
        repo.commit()
        return return_on_success

    # Note: on validation, form.duplicated_term may be set.
    # See DUPLICATE_TERM_CHECK comments in other files.

    hide_pronunciation = False
    term_language = term._language  # pylint: disable=protected-access

    if term_language is not None:
        hide_pronunciation = not term_language.show_romanization

    # Set the language dropdown to the user's current_language_id IF APPLICABLE.
    if embedded_in_reading_frame or term_language is not None:
        # Do nothing.  The language dropdown is not shown, or the term already
        # has a language assigned, and we shouldn't change it.
        pass
    else:
        # The language select control is shown and this is a new term,
        # so use the default value.
        current_language_id = int(UserSetting.get_value("current_language_id"))
        form.language_id.data = current_language_id

    return render_template(
        form_template_name,
        form=form,
        term=term,
        duplicated_term=form.duplicated_term,
        language_dicts=Language.all_dictionaries(),
        hide_pronunciation=hide_pronunciation,
        tags=repo.get_term_tags(),
        embedded_in_reading_frame=embedded_in_reading_frame,
    )


def _handle_form(term, repo, redirect_to="/term/index"):
    """
    Handle the form post, redirecting to specified url.
    """
    return handle_term_form(
        term, repo, "/term/formframes.html", redirect(redirect_to, 302)
    )


@bp.route("/edit/<int:termid>", methods=["GET", "POST"])
def edit(termid):
    """
    Edit a term.
    """
    repo = Repository(db)
    term = repo.load(termid)
    if term.status == 0:
        term.status = 1
    return _handle_form(term, repo)


@bp.route("/editbytext/<int:langid>/<text>", methods=["GET", "POST"])
def edit_by_text(langid, text):
    """
    Edit a term.
    """
    repo = Repository(db)
    term = repo.find_or_new(langid, text)
    if term.status == 0:
        term.status = 1
    return _handle_form(term, repo)


@bp.route("/new", methods=["GET", "POST"])
def new():
    """
    Create a term.
    """
    repo = Repository(db)
    term = Term()
    return _handle_form(term, repo, "/term/new")


@bp.route("/search/<text>/<int:langid>", methods=["GET"])
def search_by_text_in_language(text, langid):
    "JSON data for parent data."
    if text.strip() == "" or langid == 0:
        return []
    repo = Repository(db)
    matches = repo.find_matches(langid, text)

    def _make_entry(t):
        return {
            "id": t.id,
            "text": t.text,
            "translation": t.translation,
            "status": t.status,
        }

    result = [_make_entry(t) for t in matches]
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
    """
    Update the statuses.

    json:
    {
      updates: [ { new_status: 1, termids: [ 42, ] }, ... }, ]
    }
    """
    repo = Repository(db)

    data = request.get_json()
    updates = data.get("updates")

    for u in updates:
        new_status = int(u.get("new_status"))
        termids = u.get("termids")
        for tidstring in termids:
            term = repo.load(int(tidstring))
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
    parent = None
    repo = Repository(db)
    for tid in termids:
        term = repo.load(int(tid))
        if parent is None:
            parent = repo.find(term.language_id, parenttext)
        if term.parents != [parenttext]:
            term.parents = [parenttext]
            term.status = parent.status
            term.sync_status = True
        repo.add(term)
    repo.commit()
    return jsonify("ok")


@bp.route("/bulk_delete", methods=["POST"])
def bulk_delete():
    "Delete terms."
    data = request.get_json()
    termids = data.get("wordids")
    repo = Repository(db)
    for tid in termids:
        term = repo.load(int(tid))
        repo.delete(term)
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
