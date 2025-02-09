"""
Anki export.
"""

from flask import (
    Blueprint,
    request,
    jsonify,
    render_template,
    # redirect,
    flash,
)
from lute.models.repositories import UserSettingRepository
from lute.settings.forms import AnkiConnectSettingsForm
from lute.settings.current import refresh_global_settings
from lute.ankiexport.service import Service
from lute.models.srsexport import SrsExportSpec
from lute.ankiexport.exceptions import AnkiExportConfigurationError
from lute.db import db


bp = Blueprint("ankiexport", __name__, url_prefix="/ankiexport")


@bp.route("/index", methods=["GET", "POST"])
def anki_index():
    "Edit settings."
    repo = UserSettingRepository(db.session)
    settings = [
        "ankiconnect_web_bind_address",
        "ankiconnect_web_bind_port",
    ]
    settings_dict = {s: repo.get_value(s) for s in settings}

    form = AnkiConnectSettingsForm(
        data={
            "ankiconnect_web_bind_address": settings_dict[
                "ankiconnect_web_bind_address"
            ],
            "ankiconnect_web_bind_port": int(
                settings_dict["ankiconnect_web_bind_port"]
            ),
        }
    )

    if form.validate_on_submit():
        for field in ["ankiconnect_web_bind_address", "ankiconnect_web_bind_port"]:
            repo.set_value(field, str(getattr(form, field).data))
        db.session.commit()
        refresh_global_settings(db.session)

        flash("AnkiConnect settings updated", "success")
        return render_template("/ankiexport/index.html", form=form)

    return render_template("/ankiexport/index.html", form=form)


def _fake_export_specs():
    "Sample mapping and terms."
    gender_card_mapping = """\
      Lute_term_id: { id }
      Front: { term }: der, die, oder das?
      Picture: { image }
      Definition: { translation }
      Back: { tags:["der", "die", "das"] } { term }
      Sentence: { sentence }
    """

    dummy_card_mapping = """\
      Lute_term_id: { id }
      Front: ___ { term }
      Picture: { image }
      Definition: { translation }
      Back: { tags:["der", "die", "das"] } { term }
      Sentence: { sentence }
    """

    plural_card_mapping = """\
      Lute_term_id: { id }
      Front: { tags:["der", "die", "das"] } { parents }, plural
      Picture: { image }
      Definition: { translation }
      Back: die { term }
      Sentence: { sentence }
    """

    all_mapping_data = [
        {
            "name": "Gender",
            "selector": 'language:"German" and tags:["der", "die", "das"] and has:image',
            "deck_name": "zzTestAnkiConnect",
            "note_type": "Lute_Basic_vocab",
            "mapping": gender_card_mapping,
            "active": True,
        },
        {
            "name": "Dummy",
            "selector": 'language:"German"',
            "deck_name": "zzTestAnkiConnect",
            "note_type": "Lute_Basic_vocab",
            "mapping": dummy_card_mapping,
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
            "mapping": plural_card_mapping,
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
