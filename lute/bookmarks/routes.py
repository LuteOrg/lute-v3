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


@bp.route("/add/<int:bookid>", methods=["POST"])
def add_bookmark(bookid):
    "Add bookmark"
    data = request.json
    pagenum = data.get("pagenum")
    title = data.get("title")

    tx = (
        db.session.query(Text)
        .filter(Text.bk_id == bookid, Text.order == pagenum)
        .first()
    )

    bookmark = TextBookmark()
    bookmark.title = title
    bookmark.tx_id = tx.id

    if bookmark.title and bookmark.tx_id:
        db.session.add(bookmark)
        db.session.commit()
        return jsonify({"success": True}, 200, {"ContentType": "application/json"})

    return jsonify({"success": False}, 200, {"ContentType": "application/json"})


@bp.route("/delete/<int:bookid>", methods=["POST"])
def delete_bookmark(bookid):
    "Delete bookmark"
    data = request.json
    pagenum = data.get("page")
    title = data.get("title")

    if title and pagenum and bookid:
        db.session.query(TextBookmark).filter(
            TextBookmark.title == title,
            TextBookmark.text.has(order=pagenum),
            TextBookmark.text.has(bk_id=bookid),
        ).delete()
        db.session.commit()
        return jsonify({"success": True}, 200, {"ContentType": "application/json"})

    return jsonify({"success": False}, 200, {"ContentType": "application/json"})


@bp.route("/edit/<int:bookid>", methods=["POST"])
def edit_bookmark(bookid):
    "Edit bookmark"
    data = request.json
    pagenum = data.get("page")
    title = data.get("title")
    new_title = data.get("new_title")

    if title and pagenum and bookid:
        db.session.query(TextBookmark).filter(
            TextBookmark.title == title,
            TextBookmark.text.has(order=pagenum),
            TextBookmark.text.has(bk_id=bookid),
        ).update({"title": new_title})
        db.session.commit()
        return jsonify({"success": True}, 200, {"ContentType": "application/json"})

    return jsonify({"success": False}, 200, {"ContentType": "application/json"})
