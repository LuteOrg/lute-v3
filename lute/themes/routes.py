"Theming routes."

from flask import Blueprint, Response, jsonify

from lute.themes.service import get_current_css, next_theme
from lute.models.setting import UserSetting
from lute.db import db

bp = Blueprint("themes", __name__, url_prefix="/theme")


@bp.route("/current", methods=["GET"])
def current_theme():
    "Return current css."
    response = Response(get_current_css(), 200)
    response.content_type = "text/css; charset=utf-8"
    return response


@bp.route("/custom_styles", methods=["GET"])
def custom_styles():
    """
    Return the custom settings for inclusion in the base.html.
    """
    css = UserSetting.get_value("custom_styles")
    response = Response(css, 200)
    response.content_type = "text/css; charset=utf-8"
    return response


@bp.route("/next", methods=["POST"])
def set_next_theme():
    "Go to next theme."
    next_theme()
    return jsonify("ok")


@bp.route("/toggle_highlight", methods=["POST"])
def toggle_highlight():
    "Fix the highlight."
    b = bool(int(UserSetting.get_value("show_highlights")))
    UserSetting.set_value("show_highlights", not b)
    db.session.commit()
    return jsonify("ok")
