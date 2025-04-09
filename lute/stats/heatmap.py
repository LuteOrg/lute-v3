# heatmap.py
from flask import Blueprint, jsonify
from sqlalchemy import text
from lute.db import db

bp = Blueprint("heatmap", __name__)

@bp.route("/api/usage/heatmap")
def usage_heatmap():
    result = (
        db.session.execute(
            text("""
                SELECT DATE(WoStatusChanged) AS day, COUNT(*) AS updates
                FROM words
                WHERE WoStatusChanged IS NOT NULL
                GROUP BY DATE(WoStatusChanged)
                ORDER BY day ASC
            """)
        )
    )
    data = {str(row[0]): row[1] for row in result}

    return jsonify(data)
