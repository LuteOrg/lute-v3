"""
/book routes.
"""

import os

from flask import (
    Blueprint,
    request,
    jsonify,
    render_template,
    redirect,
    flash,
)
from lute.utils.data_tables import DataTablesFlaskParamParser
from lute.book import service
from lute.book.datatables import get_data_tables_list
from lute.book.forms import NewBookForm, EditBookForm
import lute.utils.formutils
from lute.db import db

from lute.models.book import Book as DBBook
from lute.book.model import Book, Repository


bp = Blueprint("book", __name__, url_prefix="/book")


def datatables_source(is_archived):
    "Get datatables json for books."
    parameters = DataTablesFlaskParamParser.parse_params(request.form)
    data = get_data_tables_list(parameters, is_archived)
    return jsonify(data)


@bp.route("/datatables/active", methods=["POST"])
def datatables_active_source():
    "Datatables data for active books."
    return datatables_source(False)


@bp.route("/archived", methods=["GET"])
def archived():
    "List archived books."
    return render_template("book/index.html", status="Archived")


# Archived must be capitalized, or the ajax call 404's.
@bp.route("/datatables/Archived", methods=["POST"])
def datatables_archived_source():
    "Datatables data for archived books."
    return datatables_source(True)


def _get_file_content(filefielddata):
    """
    Get the content of the file.
    """
    _, ext = os.path.splitext(filefielddata.filename)
    ext = (ext or "").lower()
    if ext == ".txt":
        return service.get_textfile_content(filefielddata)
    if ext == ".epub":
        return service.get_epub_content(filefielddata)
    if ext == ".pdf":
        msg = """
        Note: pdf imports can be inaccurate, due to how PDFs are encoded.
        Please be aware of this while reading.
        """
        flash(msg, "notice")
        return service.get_pdf_content_from_form(filefielddata)
    raise ValueError(f'Unknown file extension "{ext}"')


def _book_from_url(url):
    "Create a new book, or flash an error if can't parse."
    b = Book()
    try:
        b = service.book_from_url(url)
    except service.BookImportException as e:
        flash(e.message, "notice")
        b = Book()
    return b


@bp.route("/new", methods=["GET", "POST"])
def new():
    "Create a new book, either from text or from a file."
    b = Book()
    import_url = request.args.get("importurl", "").strip()
    if import_url != "":
        b = _book_from_url(import_url)

    form = NewBookForm(obj=b)
    form.language_id.choices = lute.utils.formutils.language_choices()
    repo = Repository(db)

    if form.validate_on_submit():
        try:
            form.populate_obj(b)
            if form.textfile.data:
                b.text = _get_file_content(form.textfile.data)
            f = form.audiofile.data
            if f:
                b.audio_filename = service.save_audio_file(f)
            book = repo.add(b)
            repo.commit()
            return redirect(f"/read/{book.id}/page/1", 302)
        except service.BookImportException as e:
            flash(e.message, "notice")

    return render_template(
        "book/create_new.html",
        book=b,
        form=form,
        tags=repo.get_book_tags(),
        show_language_selector=True,
    )


@bp.route("/edit/<int:bookid>", methods=["GET", "POST"])
def edit(bookid):
    "Edit a book - can only change a few fields."
    repo = Repository(db)
    b = repo.load(bookid)
    form = EditBookForm(obj=b)

    if form.validate_on_submit():
        form.populate_obj(b)
        f = form.audiofile.data
        if f:
            b.audio_filename = service.save_audio_file(f)
            b.audio_bookmarks = None
            b.audio_current_pos = None
        repo.add(b)
        repo.commit()
        flash(f"{b.title} updated.")
        return redirect("/", 302)

    return render_template(
        "book/edit.html", book=b, form=form, tags=repo.get_book_tags()
    )


@bp.route("/import_webpage", methods=["GET", "POST"])
def import_webpage():
    return render_template("book/import_webpage.html")


@bp.route("/archive/<int:bookid>", methods=["POST"])
def archive(bookid):
    "Archive a book."
    b = DBBook.find(bookid)
    b.archived = True
    db.session.add(b)
    db.session.commit()
    return redirect("/", 302)


@bp.route("/unarchive/<int:bookid>", methods=["POST"])
def unarchive(bookid):
    "Archive a book."
    b = DBBook.find(bookid)
    b.archived = False
    db.session.add(b)
    db.session.commit()
    return redirect("/", 302)


@bp.route("/delete/<int:bookid>", methods=["POST"])
def delete(bookid):
    "Archive a book."
    b = DBBook.find(bookid)
    db.session.delete(b)
    db.session.commit()
    return redirect("/", 302)
