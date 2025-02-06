"""
Anki export.
"""

import random

# from flask import Blueprint, current_app, Response, request, jsonify, redirect, flash
from flask import Blueprint, request, jsonify
from lute.ankiexport.service import Service
from lute.ankiexport.exceptions import AnkiExportConfigurationError

# from lute.db import db


bp = Blueprint("ankiexport", __name__, url_prefix="/ankiexport")

# Mock messages for success and failure
SUCCESS_MESSAGES = ["Created X and Y", "Successfully processed", "Action completed"]
ERROR_MESSAGES = ["Duplicate", "Invalid ID", "Processing error"]

# pylint: disable=global-statement, broad-exception-caught, broad-exception-raised
fake_fail_counter = 0


@bp.route("/get_card_post_data", methods=["POST"])
def get_ankiconnect_post_data():
    """Get data that the client javascript will post."""
    data = request.get_json()
    word_ids = data.get("term_ids", [])
    anki_deck_names = data.get("deck_names", [])
    anki_note_types = data.get("note_types", {})
    svc = Service(anki_deck_names, anki_note_types)
    try:
        ret = svc.get_ankiconnect_post_data(word_ids)
        return jsonify(ret)
    except AnkiExportConfigurationError as ex:
        response = jsonify({"error": str(ex)})
        response.status_code = 400  # Bad Request
        return response


### REMOVE
@bp.route("/create_cards_for_term_ids", methods=["POST"])
def create_cards_for_term_ids():
    """old."""
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
