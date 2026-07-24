"""
/stats endpoints.
"""

from flask import Blueprint, render_template, jsonify, request
from lute.stats.service import (
    get_chart_data,
    get_table_data,
    get_reading_streak,
    get_new_terms,
    get_mastered_terms,
    get_heatmap_data,
    get_term_languages,
    get_term_summary,
    get_last_read_language_id,
)
from lute.db import db

bp = Blueprint("stats", __name__, url_prefix="/stats")


@bp.route("/")
def index():
    "Main page."
    read_table_data = get_table_data(db.session)
    reading_streak = get_reading_streak(db.session)
    term_languages = get_term_languages(db.session)
    default_lang_id = get_last_read_language_id(db.session)
    return render_template(
        "stats/index.html",
        read_table_data=read_table_data,
        reading_streak=reading_streak,
        term_languages=term_languages,
        default_lang_id=default_lang_id,
    )


@bp.route("/data")
def get_data():
    "Ajax call for reading stats."
    chartdata = get_chart_data(db.session)
    return jsonify(chartdata)


@bp.route("/term_data")
def get_term_data():
    "Ajax call for term-related charts."
    period = request.args.get("period", "7days")
    if period not in ("7days", "monthly"):
        period = "7days"

    lang_param = request.args.get("lang_id", "")
    lang_id = None
    if lang_param and lang_param != "all":
        try:
            lang_id = int(lang_param)
        except ValueError:
            lang_id = None

    return jsonify(
        {
            "summary": get_term_summary(db.session, lang_id),
            "new_terms": get_new_terms(db.session, period, lang_id),
            "mastered_terms": get_mastered_terms(db.session, period, lang_id),
            "heatmap": get_heatmap_data(db.session, lang_id),
        }
    )
