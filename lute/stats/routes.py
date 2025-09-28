from flask import Blueprint, jsonify, render_template, redirect, url_for
from lute.stats.service import get_reading_progress, get_streaks_data, get_table_data, get_time_tracking_data
from lute.db import db
from lute.models.reading_tracker import ReadingTracker

bp = Blueprint("stats", __name__, url_prefix="/stats")

@bp.route("/", methods=["GET"])
def index():
    """
    Show stats.
    """
    streaks_data = get_streaks_data(db.session)
    read_table_data = get_table_data(db.session)
    time_tracking_data = get_time_tracking_data(db.session)
    return render_template(
        "stats/index.html",
        streaks_data=streaks_data,
        read_table_data=read_table_data,
        time_tracking_data=time_tracking_data,
    )

@bp.route("/reading_progress", methods=["GET"])
def reading_progress():
    """
    Get the user's reading progress for the day.
    """
    progress = get_reading_progress()
    return jsonify(progress)

@bp.route("/delete_reading_entry/<int:entry_id>", methods=["POST"])
def delete_reading_entry(entry_id):
    """
    Delete a reading entry.
    """
    entry = db.session.get(ReadingTracker, entry_id)
    if entry:
        db.session.delete(entry)
        db.session.commit()
    return redirect(url_for("stats.index"))
