"""
User images routes.
"""

import os
from flask import Blueprint, send_from_directory, current_app

bp = Blueprint("userimages", __name__, url_prefix="/userimages")


@bp.route("/<int:lgid>/<path:f>", methods=["GET"])
def get_image(lgid, f):
    "Serve the image from the data/userimages directory."
    datapath = current_app.config["DATAPATH"]
    directory = os.path.join(datapath, "userimages", str(lgid))
    if not os.path.exists(os.path.join(directory, f)):
        return ""
    return send_from_directory(directory, f)
