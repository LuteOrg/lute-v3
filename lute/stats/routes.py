"""
/stats endpoints.
"""

from flask import Blueprint, render_template, jsonify, flash, redirect
from lute.stats.service import get_chart_data, get_table_data, get_time_tracking_data, get_streaks_data, get_time_chart_data
from lute.db import db

bp = Blueprint("stats", __name__, url_prefix="/stats")


@bp.route("/")
def index():
    "Main page."
    read_table_data = get_table_data(db.session)
    time_tracking_data = get_time_tracking_data(db.session)
    streaks_data = get_streaks_data(db.session)
    return render_template(
        "stats/index.html",
        read_table_data=read_table_data,
        time_tracking_data=time_tracking_data,
        streaks_data=streaks_data,
    )



@bp.route("/data")
def get_data():
    "Ajax call."
    chartdata = get_chart_data(db.session)
    timechartdata = get_time_chart_data(db.session)
    return jsonify({
        'wordcount': chartdata,
        'timetracking': timechartdata
    })

@bp.route("/delete_reading_entry/<int:entry_id>", methods=["POST"])
def delete_reading_entry(entry_id):
    "Delete a reading tracking entry."
    from lute.models.reading_tracker import ReadingTracker
    entry = db.session.get(ReadingTracker, entry_id)
    if entry:
        db.session.delete(entry)
        db.session.commit()
        flash("Entry deleted.", "success")
    else:
        flash("Entry not found.", "error")
    return redirect("/stats/", 302)

