"Theming routes."

from flask import Blueprint, Response, jsonify

from lute.themes.service import Service
from lute.models.repositories import UserSettingRepository
from lute.settings.current import current_settings
from lute.db import db

bp = Blueprint("themes", __name__, url_prefix="/theme")


@bp.route("/current", methods=["GET"])
def current_theme():
    "Return current css."
    service = Service(db.session)
    response = Response(service.get_current_css(), 200)
    response.content_type = "text/css; charset=utf-8"
    return response


@bp.route("/custom_styles", methods=["GET"])
def custom_styles():
    """
    Return the custom settings for inclusion in the base.html.
    """
    repo = UserSettingRepository(db.session)
    css = repo.get_value("custom_styles")
    response = Response(css, 200)
    response.content_type = "text/css; charset=utf-8"
    return response


@bp.route("/next", methods=["POST"])
def set_next_theme():
    "Go to next theme."
    service = Service(db.session)
    service.next_theme()
    return jsonify("ok")


@bp.route("/toggle_highlight", methods=["POST"])
def toggle_highlight():
    "Fix the highlight."
    new_setting = not current_settings["show_highlights"]
    repo = UserSettingRepository(db.session)
    repo.set_value("show_highlights", new_setting)
    db.session.commit()
    current_settings["show_highlights"] = new_setting
    return jsonify("ok")
