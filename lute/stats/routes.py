"""
/stats endpoints.
"""

from flask import Blueprint, render_template, jsonify
from lute.stats.service import get_chart_data, get_table_data

bp = Blueprint("stats", __name__, url_prefix="/stats")


@bp.route("/")
def index():
    "Main page."
    read_table_data = get_table_data()
    return render_template("stats/index.html", read_table_data=read_table_data)


@bp.route("/data")
def get_data():
    "Ajax call."
    chartdata = get_chart_data()
    return jsonify(chartdata)
