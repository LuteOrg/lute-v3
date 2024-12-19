"""
/term routes.
"""

import os
import csv
import json
from flask import (
    Blueprint,
    request,
    jsonify,
    render_template,
    redirect,
    current_app,
    send_file,
    flash,
)
from lute.models.language import Language
from lute.models.term import Status
from lute.models.repositories import (
    LanguageRepository,
    TermRepository,
    UserSettingRepository,
)
from lute.utils.data_tables import DataTablesFlaskParamParser
from lute.term.datatables import get_data_tables_list
from lute.term.model import Repository, Term
from lute.term.service import (
    Service as TermService,
    TermServiceException,
    BulkTermUpdateData,
)
from lute.db import db
from lute.term.forms import TermForm
import lute.utils.formutils

bp = Blueprint("term", __name__, url_prefix="/term")


@bp.route("/index", defaults={"search": None}, methods=["GET"])
@bp.route("/index/<search>", methods=["GET"])
def index(search):
    "Index page."
    repo = TermRepository(db.session)
    repo.delete_empty_images()
    languages = db.session.query(Language).order_by(Language.name).all()
    langopts = [(lang.id, lang.name) for lang in languages]
    langopts = [(0, "(all)")] + langopts
    statuses = [s for s in db.session.query(Status).all() if s.id != Status.UNKNOWN]
    r = Repository(db.session)
    return render_template(
        "term/index.html",
        initial_search=search,
        language_options=langopts,
        statuses=statuses,
        tags=r.get_term_tags(),
        in_term_index_listing=True,
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
    data = get_data_tables_list(parameters, db.session)
    return jsonify(data)


def get_bulk_update_from_form(form):
    "Load the BulkTermUpdateData from the _bulk_edit_form_fields.html form."
    bud = BulkTermUpdateData()
    term_ids = form.get("term_ids").strip()
    if term_ids == "":
        return bud
    bud.term_ids = [int(tid.strip()) for tid in term_ids.split(",")]

    bud.lowercase_terms = form.get("lowercase_terms", "off") == "on"
    bud.remove_parents = form.get("remove_parents", "off") == "on"
    pdata = []
    if form.get("parent", "") != "":
        pdata = json.loads(form.get("parent"))
    if len(pdata) == 1:
        pdata = pdata[0]
        bud.parent_text = pdata.get("value")
        if "id" in pdata:
            bud.parent_id = int(pdata.get("id"))

    bud.change_status = form.get("change_status", "off") == "on"
    if "status" in form:
        bud.status_value = int(form.get("status"))

    def _get_tags(form_field_name):
        if form.get(form_field_name, "") == "":
            return []
        return [td["value"] for td in json.loads(form.get(form_field_name))]

    bud.add_tags = _get_tags("add_tags")
    bud.remove_tags = _get_tags("remove_tags")

    return bud


@bp.route("/bulk_edit_from_index", methods=["POST"])
def bulk_edit_from_index():
    "Edit from the term index listing."
    bud = get_bulk_update_from_form(request.form)
    svc = TermService(db.session)
    try:
        svc.apply_bulk_updates(bud)
    except TermServiceException as ex:
        flash(f"Error: {str(ex)}", "notice")
    return redirect("/term/index", 302)


@bp.route("/bulk_edit_from_reading_pane", methods=["POST"])
def bulk_edit_from_reading_pane():
    "Reading pane updates requires special redirect."
    bud = get_bulk_update_from_form(request.form)
    svc = TermService(db.session)
    try:
        svc.apply_bulk_updates(bud)
    except TermServiceException as ex:
        flash(f"Error: {str(ex)}", "notice")
        return redirect("/read/term_bulk_edit_form", 302)
    return render_template("/read/updated.html", term_text=None)


@bp.route("/export_terms", methods=["POST"])
def export_terms():
    "Generate export file of terms."
    parameters = DataTablesFlaskParamParser.parse_params(request.form)
    _load_term_custom_filters(request.form, parameters)
    parameters["length"] = 1000000
    outfile = os.path.join(current_app.env_config.temppath, "export_terms.csv")
    data = get_data_tables_list(parameters, db.session)
    term_data = data["data"]

    # Term data is an array of dicts, with the sql field name as dict
    # keys.  These need to be mapped to headings.
    heading_to_fieldname = {
        "term": "WoText",
        "parent": "ParentText",
        "translation": "WoTranslation",
        "language": "LgName",
        "tags": "TagList",
        "added": "WoCreated",
        "status": "StID",
        "link_status": "SyncStatus",
        "pronunciation": "WoRomanization",
    }

    headings = heading_to_fieldname.keys()
    output_data = [
        [r[heading_to_fieldname[fieldname]] for fieldname in headings]
        for r in term_data
    ]
    with open(outfile, "w", encoding="utf-8", newline="") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(headings)
        csv_writer.writerows(output_data)

    return send_file(outfile, as_attachment=True, download_name="Terms.csv")


def handle_term_form(
    term,
    repo,
    session,
    form_template_name,
    return_on_success,
    embedded_in_reading_frame=False,
):  # pylint: disable=too-many-arguments,too-many-positional-arguments
    """
    Handle a form post.

    This is used here and in read.routes -- read.routes.term_form
    lives in an iframe in the reading frames and returns a different
    template on success.
    """
    form = TermForm(obj=term, session=session)

    # Flash messages get added on things like term imports.
    # The user opening the form is treated as an acknowledgement.
    term.flash_message = None

    form.language_id.choices = lute.utils.formutils.language_choices(session)

    if form.validate_on_submit():
        form.populate_obj(term)
        repo.add(term)
        repo.commit()
        return return_on_success

    # Note: on validation, form.duplicated_term may be set.
    # See DUPLICATE_TERM_CHECK comments in other files.

    hide_pronunciation = False
    language_repo = LanguageRepository(session)
    term_language = language_repo.find(
        term.language_id or -1
    )  # -1 hack for no lang set.
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
        us_repo = UserSettingRepository(db.session)
        current_language_id = int(us_repo.get_value("current_language_id"))
        form.language_id.data = current_language_id

    return render_template(
        form_template_name,
        form=form,
        term=term,
        duplicated_term=form.duplicated_term,
        language_dicts=language_repo.all_dictionaries(),
        hide_pronunciation=hide_pronunciation,
        tags=repo.get_term_tags(),
        embedded_in_reading_frame=embedded_in_reading_frame,
    )


def _handle_form(term, repo, redirect_to="/term/index"):
    """
    Handle the form post, redirecting to specified url.
    """
    return handle_term_form(
        term, repo, db.session, "/term/form.html", redirect(redirect_to, 302)
    )


@bp.route("/edit/<int:termid>", methods=["GET", "POST"])
def edit(termid):
    """
    Edit a term.
    """
    repo = Repository(db.session)
    term = repo.load(termid)
    if term.status == 0:
        term.status = 1
    return _handle_form(term, repo)


@bp.route("/editbytext/<int:langid>/<text>", methods=["GET", "POST"])
def edit_by_text(langid, text):
    """
    Edit a term.
    """
    repo = Repository(db.session)
    term = repo.find_or_new(langid, text)
    if term.status == 0:
        term.status = 1
    return _handle_form(term, repo)


@bp.route("/new", methods=["GET", "POST"])
def new():
    """
    Create a term.
    """
    repo = Repository(db.session)
    term = Term()
    return _handle_form(term, repo, "/term/new")


@bp.route("/search/<text>/<int:langid>", methods=["GET"])
def search_by_text_in_language(text, langid):
    "JSON data for parent data."
    if text.strip() == "" or langid == 0:
        return []
    repo = Repository(db.session)
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
    repo = Repository(db.session)
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
    repo = Repository(db.session)

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


@bp.route("/bulk_delete", methods=["POST"])
def bulk_delete():
    "Delete terms."
    data = request.get_json()
    termids = data.get("wordids")
    repo = Repository(db.session)
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
    repo = Repository(db.session)
    term = repo.load(termid)
    repo.delete(term)
    repo.commit()
    return redirect("/term/index", 302)
