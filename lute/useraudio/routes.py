"""
User audio routes.

User audio files are stored in the database in books table.
"""

import os
from flask import Blueprint, send_file, current_app
from lute.models.book import Book

bp = Blueprint("useraudio", __name__, url_prefix="/useraudio")


@bp.route("/stream/<int:bookid>", methods=["GET"])
def stream(bookid):
    "Serve the audio, no caching."
    dirname = current_app.env_config.useraudiopath
    b = Book.find(bookid)
    fname = os.path.join(dirname, b.audio_filename)
    return send_file(fname, as_attachment=True, max_age=0)
