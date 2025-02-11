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
from lute.models.repositories import UserSettingRepository
from lute.settings.forms import AnkiConnectSettingsForm
from lute.settings.current import refresh_global_settings
from lute.ankiexport.service import Service
from lute.models.srsexport import SrsExportSpec
from lute.ankiexport.forms import SrsExportSpecForm
from lute.ankiexport.exceptions import AnkiExportConfigurationError
from lute.db import db


bp = Blueprint("ankiexport", __name__, url_prefix="/ankiexport")


@bp.route("/index", methods=["GET", "POST"])
def anki_index():
    "Edit settings."
    repo = UserSettingRepository(db.session)
    fname = "ankiconnect_url"
    url = repo.get_value(fname)
    form = AnkiConnectSettingsForm(data={fname: url})

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

    if form.validate_on_submit():
        repo.set_value(fname, form.ankiconnect_url.data)
        db.session.commit()
        refresh_global_settings(db.session)

        flash("AnkiConnect URL updated", "success")

    return render_template(
        "/ankiexport/index.html",
        form=form,
        export_specs_json=export_specs_json,
    )


def _handle_form(spec, form_template_name):
    """
    Handle a form post.
    """
    form = SrsExportSpecForm(obj=spec)

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
    return _handle_form(spec, "/ankiexport/new.html")


@bp.route("/spec/delete/<int:spec_id>", methods=["GET", "POST"])
def delete_spec(spec_id):
    "Delete a spec."
    spec = db.session.query(SrsExportSpec).filter(SrsExportSpec.id == spec_id).first()
    db.session.delete(spec)
    db.session.commit()
    flash("Export mapping deleted.")
    return redirect(f"/ankiexport/index", 302)


def _fake_export_specs():
    "Sample mapping and terms."
    gender_card_mapping = {
        "Lute_term_id": "{ id }",
        "Front": "{ term }: der, die, oder das?",
        "Picture": "{ image }",
        "Definition": "{ translation }",
        "Back": '{ tags:["der", "die", "das"] } { term }',
        "Sentence": "{ sentence }",
    }

    dummy_card_mapping = {
        "Lute_term_id": "{ id }",
        "Front": "___ { term }",
        "Picture": "{ image }",
        "Definition": "{ translation }",
        "Back": '{ tags:["der", "die", "das"] } { term }',
        "Sentence": "{ sentence }",
    }

    plural_card_mapping = {
        "Lute_term_id": "{ id }",
        "Front": '{ tags:["der", "die", "das"] } { parents }, plural',
        "Picture": "{ image }",
        "Definition": "{ translation }",
        "Back": "die { term }",
        "Sentence": "{ sentence }",
    }

    all_mapping_data = [
        {
            "name": "Gender",
            "selector": 'language:"German" and tags:["der", "die", "das"] and has:image',
            "deck_name": "zzTestAnkiConnect",
            "note_type": "Lute_Basic_vocab",
            "mapping": json.dumps(gender_card_mapping),
            "active": True,
        },
        {
            "name": "Dummy",
            "selector": 'language:"German"',
            "deck_name": "zzTestAnkiConnect",
            "note_type": "Lute_Basic_vocab",
            "mapping": json.dumps(dummy_card_mapping),
            "active": True,
        },
        {
            "name": "Pluralization",
            "selector": (
                'language:"German" and parents.count = 1 '
                + 'and has:image and tags:["plural", "plural and singular"]'
            ),
            "deck_name": "zzTestAnkiConnect",
            "note_type": "Lute_Basic_vocab",
            "mapping": json.dumps(plural_card_mapping),
            "active": True,
        },
        {
            "name": "m3",
            "selector": "sel here",
            "deck_name": "x",
            "note_type": "y",
            "mapping": "some mapping here",
            "active": False,
        },
    ]

    export_specs = []
    for md in all_mapping_data:
        spec = SrsExportSpec()
        spec.id = len(export_specs) + 1
        spec.export_name = md["name"]
        spec.criteria = md["selector"]
        spec.deck_name = md["deck_name"]
        spec.note_type = md["note_type"]
        spec.field_mapping = md["mapping"]
        spec.active = md["active"]
        export_specs.append(spec)

    active_specs = [m for m in export_specs if m.active]
    return active_specs


def get_active_export_specs():
    """
    Get data.

    Hardcoded fake data for now.

    TODO - change to db fetch
    """
    return _fake_export_specs()


# TODO - search for get_card_post_data, hook it up
# lute.js
# term index.js?
@bp.route("/get_card_post_data", methods=["POST"])
def get_ankiconnect_post_data():
    """Get data that the client javascript will post."""
    data = request.get_json()
    word_ids = data["term_ids"]
    base_url = data["base_url"]
    anki_deck_names = data["deck_names"]
    anki_note_types = data["note_types"]
    export_specs = get_active_export_specs()
    svc = Service(anki_deck_names, anki_note_types, export_specs)
    try:
        ret = svc.get_ankiconnect_post_data(word_ids, base_url, db.session)
        return jsonify(ret)
    except AnkiExportConfigurationError as ex:
        response = jsonify({"error": str(ex)})
        response.status_code = 400  # Bad Request
        return response
