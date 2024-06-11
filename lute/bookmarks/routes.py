"""
/bookmarks endpoint
"""

from flask import Blueprint, request, render_template, jsonify
from lute.bookmarks.datatables import get_data_tables_list
from lute.models.book import Book, Text, TextBookmark
from lute.utils.data_tables import DataTablesFlaskParamParser
from lute.db import db

bp = Blueprint("bookmarks", __name__, url_prefix="/bookmarks")


@bp.route("/<int:bookid>/datatables", methods=["POST"])
def datatables_bookmarks(bookid):
    "Get datatables json for bookmarks."
    parameters = DataTablesFlaskParamParser.parse_params(request.form)
    data = get_data_tables_list(parameters, bookid)
    return jsonify(data)


@bp.route("/<int:bookid>", methods=["GET"])
def bookmarks(bookid):
    "Get all bookarks for given bookid."
    book = Book.find(bookid)

    text_dir = "rtl" if book.language.right_to_left else "ltr"
    return render_template("bookmarks/list.html", book=book, text_dir=text_dir)


@bp.route("/add", methods=["POST"])
def add_bookmark():
    "Add bookmark"
    data = request.json
    title = data.get("title")
    try:
        book_id = int(data.get("book_id"))
        page_num = int(data.get("page_num"))
    except ValueError:
        return jsonify(
            success=False, reason="Invalid book_id or page_num provided.", status=200
        )

    if book_id is None or page_num is None or title is None:
        return jsonify(
            success=False,
            reason="Missing value for required parameter 'title' or 'book_id' or page_num.",
            status=200,
        )

    tx = (
        db.session.query(Text)
        .filter(Text.bk_id == book_id)
        .filter(Text.order == page_num)
        .first()
    )
    bookmark = TextBookmark(title=title, text=tx)

    db.session.add(bookmark)
    db.session.commit()
    return jsonify(success=True, status=200)


@bp.route("/delete", methods=["POST"])
def delete_bookmark():
    "Delete bookmark"
    data = request.json
    bookmark_id = None
    try:
        bookmark_id = int(data.get("bookmark_id"))
    except ValueError:
        return jsonify(
            success=False,
            reason=f"Invalid bookmark_id ({data.get('bookmark_id')}) provided.",
            status=200,
        )

    if bookmark_id is None:
        return jsonify(
            success=False,
            reason="Missing required parameter 'bookmark_id'.",
            status=200,
        )

    db.session.query(TextBookmark).filter(TextBookmark.id == bookmark_id).delete()
    db.session.commit()
    return jsonify(success=True, status=200)


@bp.route("/edit", methods=["POST"])
def edit_bookmark():
    "Edit bookmark"
    data = request.json
    bookmark_id = None
    try:
        bookmark_id = int(data.get("bookmark_id"))
    except ValueError:
        return jsonify(
            success=False, reason="Invalid bookmark_id provided.", status=200
        )
    new_title = data.get("new_title", "").strip()

    if bookmark_id is None or new_title == "":
        return jsonify(
            success=False,
            reason="Missing value for required parameter 'new_title' or 'bookmark_id'.",
            status=200,
        )

    db.session.query(TextBookmark).filter(TextBookmark.id == bookmark_id).update(
        {"title": new_title}
    )
    db.session.commit()
    return jsonify(success=True, status=200)
