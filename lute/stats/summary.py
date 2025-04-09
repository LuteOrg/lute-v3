# summary.py
from flask import Blueprint, jsonify
from sqlalchemy import text
from lute.db import db

bp = Blueprint("summary", __name__)

@bp.route("/api/usage/summary")
def usage_summary():
    result = db.session.execute(text("""
        SELECT
            (SELECT COUNT(*) FROM words) AS total_words,
            (SELECT SUM(TxWordCount) FROM texts WHERE TxWordCount IS NOT NULL) AS total_text_words,
            (SELECT COUNT(*) FROM words WHERE WoStatus = 5) AS known_words,
            (SELECT COUNT(*) FROM words WHERE WoStatus = 2) AS learning_words,
            (SELECT COUNT(*) FROM words WHERE WoStatus = 1) AS unknown_words,
            (SELECT COUNT(*) FROM words WHERE WoCreated >= DATE('now', '-30 days')) AS words_added_30d,
            (SELECT COUNT(*) FROM words WHERE WoStatusChanged >= DATE('now', '-30 days')) AS status_changed_30d
    """)).first()

    data = {
        "total_words": result.total_words,
        "total_text_words": result.total_text_words,
        "known_words": result.known_words,
        "learning_words": result.learning_words,
        "unknown_words": result.unknown_words,
        "words_added_30d": result.words_added_30d,
        "status_changed_30d": result.status_changed_30d,
    }

    return jsonify(data)


@bp.route("/api/usage/words_by_book")
def words_by_book():
    result = db.session.execute(text("""
        SELECT books.BkTitle, SUM(texts.TxWordCount) AS word_count
        FROM texts
        JOIN books ON texts.TxBkID = books.BkID
        WHERE texts.TxWordCount IS NOT NULL
        GROUP BY books.BkID
        ORDER BY word_count DESC
    """))
    
    data = [{"title": row[0], "words": row[1]} for row in result]
    return jsonify(data)

@bp.route("/api/usage/new_words_by_day")
def new_words_by_day():
    result = db.session.execute(text("""
        SELECT DATE(WoCreated) AS day, COUNT(*) AS count
        FROM words
        WHERE WoCreated IS NOT NULL
        GROUP BY DATE(WoCreated)
        ORDER BY day ASC
    """))

    data = [{"date": str(row.day), "count": row.count} for row in result]
    return jsonify(data)
