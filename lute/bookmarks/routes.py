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
        return jsonify(success=False, reason="Invalid Text ID provided.", status=200)

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
    bookmark = TextBookmark(title=title, tx_id=tx.id)

    db.session.add(bookmark)
    db.session.commit()
    return jsonify(success=True, status=200)


@bp.route("/delete", methods=["POST"])
def delete_bookmark():
    "Delete bookmark"
    data = request.json
    title = data.get("title")
    try:
        text_id = int(data.get("text_id"))
    except ValueError:
        return jsonify(
            success=False,
            reason=f"Invalid Text ID ({data.get('text_id')}) provided.",
            status=200,
        )

    if not title or not text_id:
        return jsonify(
            success=False,
            reason="Missing value for required parameter 'title' or 'text_id'.",
            status=200,
        )

    db.session.query(TextBookmark).filter(
        TextBookmark.title == title,
        TextBookmark.text.has(id=text_id),
    ).delete()
    db.session.commit()
    return jsonify(success=True, status=200)


@bp.route("/edit", methods=["POST"])
def edit_bookmark():
    "Edit bookmark"
    data = request.json
    try:
        text_id = int(data.get("text_id"))
    except ValueError:
        return jsonify(success=False, reason="Invalid Text ID provided.", status=200)
    title = data.get("title")
    new_title = data.get("new_title")

    if not title or not text_id:
        return jsonify(
            success=False,
            reason="Missing value for required parameter 'title' or 'text_id'.",
            status=200,
        )

    db.session.query(TextBookmark).filter(
        TextBookmark.title == title,
        TextBookmark.text.has(id=text_id),
    ).update({"title": new_title})
    db.session.commit()
    return jsonify(success=True, status=200)
