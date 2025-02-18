"""
Anki export.
"""

import json
from flask import (
    Blueprint,
    request,
    jsonify,
    render_template,
    redirect,
    flash,
)
from lute.ankiexport.service import Service
from lute.models.srsexport import SrsExportSpec
from lute.ankiexport.forms import SrsExportSpecForm
from lute.ankiexport.exceptions import AnkiExportConfigurationError
from lute.db import db


bp = Blueprint("ankiexport", __name__, url_prefix="/ankiexport")


@bp.route("/index", methods=["GET", "POST"])
def anki_index():
    "List the exports."
    export_specs = db.session.query(SrsExportSpec).all()
    export_specs_json = [
        {
            "id": spec.id,
            "export_name": spec.export_name,
            "criteria": spec.criteria,
            "deck_name": spec.deck_name,
            "note_type": spec.note_type,
            "field_mapping": spec.field_mapping,
            "active": "yes" if spec.active else "no",
        }
        for spec in export_specs
    ]

    return render_template(
        "/ankiexport/index.html",
        export_specs_json=export_specs_json,
    )


def _handle_form(spec, form_template_name):
    """
    Handle a form post.
    """
    form = SrsExportSpecForm(obj=spec)

    if request.method == "POST":
        anki_settings_json = request.form.get("ankisettings")
        anki_settings = json.loads(anki_settings_json)

        form.anki_deck_names = anki_settings.get("deck_names")
        form.anki_note_types = anki_settings.get("note_types")

        # Have to load the option choices or flask-wtf complains ...
        # ouch.
        form.deck_name.choices = [(f, f) for f in form.anki_deck_names]
        form.note_type.choices = [(f, f) for f in form.anki_note_types.keys()]

    if form.validate_on_submit():
        form.populate_obj(spec)
        db.session.add(spec)
        db.session.commit()
        return redirect("/ankiexport/index", 302)

    return render_template(form_template_name, form=form, spec=spec)


@bp.route("/spec/edit/<int:spec_id>", methods=["GET", "POST"])
def edit_spec(spec_id):
    "Edit a spec."
    spec = db.session.query(SrsExportSpec).filter(SrsExportSpec.id == spec_id).first()
    return _handle_form(spec, "/ankiexport/edit.html")


@bp.route("/spec/new", methods=["GET", "POST"])
def new_spec():
    "Make a new spec."
    spec = SrsExportSpec()
    # Hack ... not sure why this was necessary, given that the model
    # and form both have the default as True.
    if spec.active is None:
        spec.active = True
    return _handle_form(spec, "/ankiexport/new.html")


@bp.route("/spec/delete/<int:spec_id>", methods=["GET", "POST"])
def delete_spec(spec_id):
    "Delete a spec."
    spec = db.session.query(SrsExportSpec).filter(SrsExportSpec.id == spec_id).first()
    db.session.delete(spec)
    db.session.commit()
    flash("Export mapping deleted.")
    return redirect("/ankiexport/index", 302)


@bp.route("/get_card_post_data", methods=["POST"])
def get_ankiconnect_post_data():
    """Get data that the client javascript will post."""
    data = request.get_json()
    word_ids = data["term_ids"]
    termid_sentences = data["termid_sentences"]
    base_url = data["base_url"]
    anki_deck_names = data["deck_names"]
    anki_note_types = data["note_types"]
    export_specs = db.session.query(SrsExportSpec).all()
    svc = Service(anki_deck_names, anki_note_types, export_specs)
    try:
        ret = svc.get_ankiconnect_post_data(
            word_ids, termid_sentences, base_url, db.session
        )
        return jsonify(ret)
    except AnkiExportConfigurationError as ex:
        response = jsonify({"error": str(ex)})
        response.status_code = 400  # Bad Request
        return response


@bp.route("/validate_export_specs", methods=["POST"])
def validate_export_specs():
    """Get data that the client javascript will post."""
    data = request.get_json()
    anki_deck_names = data["deck_names"]
    anki_note_types = data["note_types"]
    export_specs = db.session.query(SrsExportSpec).all()
    svc = Service(anki_deck_names, anki_note_types, export_specs)
    try:
        ret = svc.validate_specs()
        return jsonify(ret)
    except AnkiExportConfigurationError as ex:
        response = jsonify({"error": str(ex)})
        response.status_code = 400  # Bad Request
        return response
