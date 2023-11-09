"""
/read endpoints.
"""

from datetime import datetime

from flask import Blueprint, render_template, redirect
from lute.read.service import get_paragraphs, set_unknowns_to_known
from lute.read.forms import TextForm
from lute.term.model import Repository
from lute.term.routes import handle_term_form
from lute.models.book import Book, Text
from lute.models.term import Term as DBTerm
from lute.book.stats import mark_stale
from lute.db import db


bp = Blueprint("read", __name__, url_prefix="/read")


def _page_in_range(book, n):
    "Return the page number respecting the page range."
    ret = max(n, 1)
    ret = min(ret, book.page_count)
    return ret


@bp.route("/<int:bookid>/page/<int:pagenum>", methods=["GET"])
def read(bookid, pagenum):
    "Display reading pane for book page."

    book = Book.find(bookid)
    lang = book.language

    pagenum = _page_in_range(book, pagenum)
    text = book.texts[pagenum - 1]
    book.current_tx_id = text.id
    db.session.add(book)
    db.session.commit()

    paragraphs = get_paragraphs(text)

    prevpage = _page_in_range(book, pagenum - 1)
    nextpage = _page_in_range(book, pagenum + 1)
    prev10 = _page_in_range(book, pagenum - 10)
    next10 = _page_in_range(book, pagenum + 10)

    mark_stale(book)

    return render_template(
        "read/index.html",
        hide_top_menu=True,
        text=text,
        textid=text.id,
        is_rtl=lang.right_to_left,
        html_title=text.title,
        book=book,
        dictionary_url=lang.sentence_translate_uri,
        pagenum=pagenum,
        pagecount=book.page_count,
        prevpage=prevpage,
        prev10page=prev10,
        nextpage=nextpage,
        next10page=next10,
        paragraphs=paragraphs,
    )


def _process_footer_action(bookid, pagenum, nextpage, set_to_known=True):
    """ "
    Mark as read,
    optionally mark all terms as known on the current page,
    and go to the next page.
    """
    book = Book.find(bookid)
    pagenum = _page_in_range(book, pagenum)
    text = book.texts[pagenum - 1]
    text.read_date = datetime.now()
    db.session.add(text)
    db.session.commit()
    if set_to_known:
        set_unknowns_to_known(text)
    return redirect(f"/read/{bookid}/page/{nextpage}", code=302)


@bp.route("/<int:bookid>/page/<int:pagenum>/allknown/<int:nextpage>", methods=["post"])
def allknown(bookid, pagenum, nextpage):
    "Mark all as known, go to next page."
    return _process_footer_action(bookid, pagenum, nextpage, True)


@bp.route("/<int:bookid>/page/<int:pagenum>/markread/<int:nextpage>", methods=["post"])
def mark_read(bookid, pagenum, nextpage):
    "Mark page as read, go to the next page."
    return _process_footer_action(bookid, pagenum, nextpage, False)


@bp.route("/sentences/<int:textid>", methods=["GET"])
def sentences(textid):
    "Display sentences for the given text."
    text = db.session.query(Text).filter(Text.id == textid).first()
    paragraphs = get_paragraphs(text)
    return render_template("read/sentences.html", paragraphs=paragraphs)


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


@bp.route("/editpage/<int:textid>", methods=["GET", "POST"])
def edit_page(textid):
    "Edit the text on a page."
    text = db.session.get(Text, textid)
    if text is None:
        return redirect("/", 302)
    form = TextForm(obj=text)

    if form.validate_on_submit():
        form.populate_obj(text)
        db.session.add(text)
        db.session.commit()
        return redirect(f"/read/{text.book.id}/page/{text.order}", 302)

    return render_template("read/page_edit_form.html", hide_top_menu=True, form=form)
