"""
Anki export.
"""

import random
from flask import Blueprint, current_app, Response, request, jsonify, redirect, flash
from lute.db import db


bp = Blueprint("ankiexport", __name__, url_prefix="/ankiexport")

# Mock messages for success and failure
SUCCESS_MESSAGES = ["Created X and Y", "Successfully processed", "Action completed"]
ERROR_MESSAGES = ["Duplicate", "Invalid ID", "Processing error"]

fake_fail_counter = 0


@bp.route("/create_cards_for_term_ids", methods=["POST"])
def create_cards_for_term_ids():
    global fake_fail_counter
    data = request.get_json()
    word_ids = data.get("term_ids", [])

    results = []
    for word_id in word_ids:
        fake_fail_counter += 1
        if fake_fail_counter % 2 == 0:  # Even IDs succeed
            message = random.choice(SUCCESS_MESSAGES)
            results.append({"word-id": word_id, "message": message, "error": None})
        else:  # Odd IDs fail
            error = random.choice(ERROR_MESSAGES)
            results.append({"word-id": word_id, "message": "", "error": error})

    return jsonify(results)
