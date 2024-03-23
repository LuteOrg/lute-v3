"""
/read endpoints.
"""

from datetime import datetime
from flask import Blueprint, flash, request, render_template, redirect, jsonify
from lute.read.service import set_unknowns_to_known, start_reading, get_popup_data
from lute.read.forms import TextForm
from lute.term.model import Repository
from lute.term.routes import handle_term_form
from lute.models.book import Book, Text
from lute.models.setting import UserSetting
from lute.db import db


bp = Blueprint("read", __name__, url_prefix="/read")


def _render_book_page(book, pagenum):
    """
    Render a particular book page.
    """
    lang = book.language
    show_highlights = bool(int(UserSetting.get_value("show_highlights")))
    term_dicts = lang.all_dictionaries()[lang.id]["term"]

    return render_template(
        "read/index.html",
        hide_top_menu=True,
        is_rtl=lang.right_to_left,
        html_title=book.title,
        book=book,
        sentence_dict_uris=lang.sentence_dict_uris,
        page_num=pagenum,
        page_count=book.page_count,
        show_highlights=show_highlights,
        lang_id=lang.id,
        term_dicts=term_dicts,
    )


@bp.route("/<int:bookid>", methods=["GET"])
def read(bookid):
    """
    Read a book, opening to its current page.

    This is called from the book listing, on Lute index.
    """
    book = Book.find(bookid)
    if book is None:
        flash(f"No book matching id {bookid}")
        return redirect("/", 302)

    page_num = 1
    text = book.texts[0]
    if book.current_tx_id:
        text = Text.find(book.current_tx_id)
        page_num = text.order

    return _render_book_page(book, page_num)


@bp.route("/<int:bookid>/page/<int:pagenum>", methods=["GET"])
def read_page(bookid, pagenum):
    """
    Read a particular page of a book.

    Called from term Sentences link.
    """
    book = Book.find(bookid)
    if book is None:
        flash(f"No book matching id {bookid}")
        return redirect("/", 302)

    pagenum = book.page_in_range(pagenum)
    return _render_book_page(book, pagenum)


@bp.route("/page_done", methods=["post"])
def page_done():
    "Handle POST when page is done."
    data = request.json
    bookid = int(data.get("bookid"))
    pagenum = int(data.get("pagenum"))
    restknown = data.get("restknown")

    book = Book.find(bookid)
    text = book.text_at_page(pagenum)
    text.read_date = datetime.now()
    db.session.add(text)
    db.session.commit()
    if restknown:
        set_unknowns_to_known(text)
    return jsonify("ok")


@bp.route("/delete_page/<int:bookid>/<int:pagenum>", methods=["GET"])
def delete_page(bookid, pagenum):
    """
    Delete page.
    """
    book = Book.find(bookid)
    if book is None:
        flash(f"No book matching id {bookid}")
        return redirect("/", 302)

    if len(book.texts) == 1:
        flash("Cannot delete only page in book.")
    else:
        book.remove_page(pagenum)
        db.session.add(book)
        db.session.commit()

    url = f"/read/{bookid}/page/{pagenum}"
    return redirect(url, 302)


@bp.route("/new_page/<int:bookid>/<position>/<int:pagenum>", methods=["GET", "POST"])
def new_page(bookid, position, pagenum):
    "Create a new page."
    form = TextForm()
    book = Book.find(bookid)

    if form.validate_on_submit():
        t = None
        if position == "before":
            t = book.add_page_before(pagenum)
        else:
            t = book.add_page_after(pagenum)
        t.book = book
        t.text = form.text.data
        db.session.add(book)
        db.session.commit()

        book.current_tx_id = t.id
        db.session.add(book)
        db.session.commit()

        return redirect(f"/read/{book.id}", 302)

    text_dir = "rtl" if book.language.right_to_left else "ltr"
    return render_template(
        "read/page_edit_form.html", hide_top_menu=True, form=form, text_dir=text_dir
    )


@bp.route("/save_player_data", methods=["post"])
def save_player_data():
    "Save current player position, bookmarks.  Called on a loop by the player."
    data = request.json
    bookid = int(data.get("bookid"))
    book = Book.find(bookid)
    book.audio_current_pos = float(data.get("position"))
    book.audio_bookmarks = data.get("bookmarks")
    db.session.add(book)
    db.session.commit()
    return jsonify("ok")


@bp.route("/renderpage/<int:bookid>/<int:pagenum>", methods=["GET"])
def render_page(bookid, pagenum):
    "Method called by ajax, render the given page."
    book = Book.find(bookid)
    if book is None:
        flash(f"No book matching id {bookid}")
        return redirect("/", 302)
    paragraphs = start_reading(book, pagenum, db.session)
    return render_template("read/page_content.html", paragraphs=paragraphs)


@bp.route("/empty", methods=["GET"])
def empty():
    "Show an empty/blank page."
    return ""


@bp.route("/termform/<int:langid>/<text>", methods=["GET", "POST"])
def term_form(langid, text):
    """
    Create a multiword term.
    """
    repo = Repository(db)
    term = repo.find_or_new(langid, text)
    if term.status == 0:
        term.status = 1
    return handle_term_form(
        term,
        repo,
        "/read/frameform.html",
        render_template("/read/updated.html", term_text=term.text),
        embedded_in_reading_frame=True,
    )


@bp.route("/edit_term/<int:term_id>", methods=["GET", "POST"])
def edit_term_form(term_id):
    """
    Edit a term.
    """
    repo = Repository(db)
    term = repo.load(term_id)
    # print(f"editing term {term_id}", flush=True)
    if term.status == 0:
        term.status = 1
    return handle_term_form(
        term,
        repo,
        "/read/frameform.html",
        render_template("/read/updated.html", term_text=term.text),
        embedded_in_reading_frame=True,
    )


@bp.route("/termpopup/<int:termid>", methods=["GET"])
def term_popup(termid):
    """
    Show a term popup for the given DBTerm.
    """
    d = get_popup_data(termid)
    return render_template(
        "read/termpopup.html",
        term=d["term"],
        flashmsg=d["flashmsg"],
        term_tags=d["term_tags"],
        term_images=d["term_images"],
        parentdata=d["parentdata"],
        parentterms=d["parentterms"],
        componentdata=d["components"],
    )


@bp.route("/flashcopied", methods=["GET"])
def flashcopied():
    return render_template("read/flashcopied.html")


@bp.route("/editpage/<int:bookid>/<int:pagenum>", methods=["GET", "POST"])
def edit_page(bookid, pagenum):
    "Edit the text on a page."
    book = Book.find(bookid)
    text = book.text_at_page(pagenum)
    if text is None:
        return redirect("/", 302)
    form = TextForm(obj=text)

    if form.validate_on_submit():
        form.populate_obj(text)
        db.session.add(text)
        db.session.commit()
        return redirect(f"/read/{book.id}", 302)

    text_dir = "rtl" if book.language.right_to_left else "ltr"
    return render_template(
        "read/page_edit_form.html", hide_top_menu=True, form=form, text_dir=text_dir
    )
