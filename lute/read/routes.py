"""
/read endpoints.
"""

from flask import Blueprint, render_template

from lute.read.service import get_paragraphs
from lute.models.book import Book, Text
from lute.db import db

bp = Blueprint('read', __name__, url_prefix='/read')

@bp.route('/<int:bookid>/page/<int:pagenum>', methods=['GET'])
def read(bookid, pagenum):
    "Display reading pane for book page."

    book = Book.find(bookid)
    lang = book.language

    def page_in_range(n):
        "Force n in range 1 to book.page_count."
        n = max(n, 1)
        n = min(n, book.page_count)
        return n

    pagenum = page_in_range(pagenum)
    text = book.texts[pagenum - 1]
    paragraphs = get_paragraphs(text)

    prevpage = page_in_range(pagenum - 1)
    nextpage = page_in_range(pagenum + 1)
    prev10 = page_in_range(pagenum - 10)
    next10 = page_in_range(pagenum + 10)

    # TODO book: set the book.currentpage db
    # facade = ReadingFacade()
    # facade.set_current_book_text(text)
    # TODO book stats: mark stale for recalc later
    # BookStats.markStale(book)

    return render_template(
        'read/index.html',
        text=text,
        textid=text.id,
        is_rtl = lang.right_to_left,
        html_title=text.title,
        book=book,
        dictionary_url = lang.sentence_translate_uri,
        pagenum=pagenum,
        pagecount=book.page_count,
        prevpage=prevpage,
        prev10page=prev10,
        nextpage=nextpage,
        next10page=next10,
        paragraphs=paragraphs)


# TODO unused code: this may not be used.
@bp.route('/text/<int:textid>', methods=['GET'])
def read_text(textid):
    "Display a text."
    text = Text.find(textid)
    lang = text.book.language
    is_rtl = lang.right_to_left
    paragraphs = get_paragraphs(text)

    return render_template(
        'read/text.html',
        textid=textid,
        is_rtl=is_rtl,
        dictionary_url = lang.sentence_translate_uri,
        paragraphs=paragraphs)


@bp.route('/sentences/<int:textid>', methods=['GET'])
def sentences(textid):
    "Display sentences for the given text."
    text = db.session.query(Text).filter(Text.id == textid).first()
    paragraphs = get_paragraphs(text)
    return render_template(
        'read/sentences.html',
        paragraphs=paragraphs)
