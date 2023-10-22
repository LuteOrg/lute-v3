"""
/read endpoints.
"""

from sqlalchemy.exc import IntegrityError

from flask import Blueprint, render_template, flash

from lute.read.service import get_paragraphs
from lute.term.model import Repository
from lute.term.forms import TermForm
from lute.models.book import Book, Text
from lute.models.term import Term as DBTerm
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


@bp.route('/empty', methods=['GET'])
def empty():
    "Show an empty/blank page."
    return ''


def _handle_form(term, form) -> bool:
    """
    Handle the read term form processing.
    Returns True if validated and saved.
    """
    if not form.validate_on_submit():
        return False

    form.populate_obj(term)
    if term.text_has_changed():
        flash('Can only change term case.', 'error')
        term.text = term.original_text
        form = TermForm(obj=term)
        return False

    ret = False
    try:
        repo = Repository(db)
        repo.add(term)
        repo.commit()

        # Don't add a flash message here.  When the reading term is
        # updated, it shows the read/updated.html template, which has
        # its own "flash" message.  Adding a flash here would send the
        # message to the base.html template.
        # flash(f'Term {term.text} updated', 'success')
        ret = True

    except IntegrityError as e:
        # TODO term: better integrity error message - currently
        # shows raw message.
        # TODO check if used: not sure if this will ever occur
        flash(e.orig.args, 'error')

    return ret


# TODO: term form: ensure reading pane can create form with "." character
@bp.route('/termform/<int:langid>/<text>', methods=['GET', 'POST'])
def term_form(langid, text):
    """
    Create or edit a term.
    """
    repo = Repository(db)
    term = repo.find_or_new(langid, text)

    form = TermForm(obj=term)
    if _handle_form(term, form):
        return render_template('/read/updated.html', term_text=term.text)

    return render_template(
        '/read/frameform.html',
        form=form,
        term=term,
        showlanguageselector=False,

        # TODO term tags: pass dynamic list.
        tags=[ "apple", "bear", "cat" ],
        parent_link_to_frame=True
    )


@bp.route('/termpopup/<int:termid>', methods=['GET'])
def term_popup(termid):
    """
    Show a term popup for the given DBTerm.
    """
    term = DBTerm.query.get(termid)

    term_tags = [tt.text for tt in term.term_tags]

    def make_array(t):
        ret = {
            'term': t.text,
            'roman': t.romanization,
            'trans': t.translation if t.translation else '-',
            'tags': [tt.text for tt in t.term_tags],
        }
        return ret

    print(term.parents)
    parent_terms = [p.text for p in term.parents]
    parent_terms = ', '.join(parent_terms)

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
        'read/termpopup.html',
        term=term,
        flashmsg=term.get_flash_message(),
        term_tags=term_tags,
        term_images=images,
        parentdata=parent_data,
        parentterms=parent_terms)


@bp.route('/keyboard_shortcuts', methods=['GET'])
def keyboard_shortcuts():
    return render_template('read/keyboard_shortcuts.html')
