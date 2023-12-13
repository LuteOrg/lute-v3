"""
/read endpoints.
"""

from datetime import datetime
from flask import Blueprint, flash, request, render_template, redirect, jsonify
from lute.read.service import get_paragraphs, set_unknowns_to_known
from lute.read.forms import TextForm
from lute.term.model import Repository
from lute.term.routes import handle_term_form
from lute.models.book import Book, Text
from lute.models.term import Term as DBTerm
from lute.models.setting import UserSetting
from lute.book.stats import mark_stale
from lute.db import db


bp = Blueprint("read", __name__, url_prefix="/read")


def _page_in_range(book, n):
    "Return the page number respecting the page range."
    ret = max(n, 1)
    ret = min(ret, book.page_count)
    return ret


def _render_book_page(book, pagenum):
    """
    Render a particular book page.
    """
    lang = book.language
    show_highlights = bool(int(UserSetting.get_value("show_highlights")))

    return render_template(
        "read/index.html",
        hide_top_menu=True,
        is_rtl=lang.right_to_left,
        html_title=book.title,
        book=book,
        dictionary_url=lang.sentence_translate_uri,
        page_num=pagenum,
        page_count=book.page_count,
        show_highlights=show_highlights,
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

    pagenum = _page_in_range(book, pagenum)
    return _render_book_page(book, pagenum)


@bp.route("/page_done", methods=["post"])
def page_done():
    "Handle POST when page is done."
    data = request.json
    bookid = int(data.get("bookid"))
    pagenum = int(data.get("pagenum"))
    restknown = data.get("restknown")

    book = Book.find(bookid)
    pagenum = _page_in_range(book, pagenum)
    text = book.texts[pagenum - 1]
    text.read_date = datetime.now()
    db.session.add(text)
    db.session.commit()
    if restknown:
        set_unknowns_to_known(text)
    return jsonify("ok")


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

    pagenum = _page_in_range(book, pagenum)
    text = book.texts[pagenum - 1]

    mark_stale(book)
    book.current_tx_id = text.id
    db.session.add(book)
    db.session.commit()

    paragraphs = get_paragraphs(text)
    return render_template("read/page_content.html", paragraphs=paragraphs)


@bp.route("/empty", methods=["GET"])
def empty():
    "Show an empty/blank page."
    return ""


@bp.route("/termform/<int:langid>/<text>", methods=["GET", "POST"])
def term_form(langid, text):
    """
    Create or edit a term.
    """
    repo = Repository(db)
    term = repo.find_or_new(langid, text)

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
    term = DBTerm.query.get(termid)

    term_tags = [tt.text for tt in term.term_tags]

    def make_array(t):
        ret = {
            "term": t.text,
            "roman": t.romanization,
            "trans": t.translation if t.translation else "-",
            "tags": [tt.text for tt in t.term_tags],
        }
        return ret

    parent_terms = [p.text for p in term.parents]
    parent_terms = ", ".join(parent_terms)

    parent_data = []
    if len(term.parents) == 1:
        parent = term.parents[0]
        if parent.translation != term.translation:
            parent_data.append(make_array(parent))
    else:
        parent_data = [make_array(p) for p in term.parents]

    images = [term.get_current_image()] if term.get_current_image() else []
    for p in term.parents:
        if p.get_current_image():
            images.append(p.get_current_image())

    images = list(set(images))

    return render_template(
        "read/termpopup.html",
        term=term,
        flashmsg=term.get_flash_message(),
        term_tags=term_tags,
        term_images=images,
        parentdata=parent_data,
        parentterms=parent_terms,
    )


@bp.route("/keyboard_shortcuts", methods=["GET"])
def keyboard_shortcuts():
    return render_template("read/keyboard_shortcuts.html")


@bp.route("/flashcopied", methods=["GET"])
def flashcopied():
    return render_template("read/flashcopied.html")


@bp.route("/editpage/<int:bookid>/<int:pagenum>", methods=["GET", "POST"])
def edit_page(bookid, pagenum):
    "Edit the text on a page."
    book = Book.find(bookid)
    pagenum = _page_in_range(book, pagenum)
    text = book.texts[pagenum - 1]
    if text is None:
        return redirect("/", 302)
    form = TextForm(obj=text)

    if form.validate_on_submit():
        form.populate_obj(text)
        db.session.add(text)
        db.session.commit()
        return redirect(f"/read/{book.id}", 302)

    return render_template("read/page_edit_form.html", hide_top_menu=True, form=form)
