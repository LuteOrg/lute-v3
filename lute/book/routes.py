"""
/book routes.
"""

import json
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

from lute.models.language import Language
from lute.models.book import Book as DBBook
from lute.models.setting import UserSetting
from lute.book.model import Book, Repository


bp = Blueprint("book", __name__, url_prefix="/book")


def _load_term_custom_filters(request_form, parameters):
    "Manually add filters that the DataTablesFlaskParamParser doesn't know about."
    filter_param_names = [
        "filtLanguage",
    ]
    request_params = request_form.to_dict(flat=True)
    for p in filter_param_names:
        parameters[p] = request_params.get(p)


def datatables_source(is_archived):
    "Get datatables json for books."
    parameters = DataTablesFlaskParamParser.parse_params(request.form)
    _load_term_custom_filters(request.form, parameters)
    data = get_data_tables_list(parameters, is_archived)
    return jsonify(data)


@bp.route("/datatables/active", methods=["POST"])
def datatables_active_source():
    "Datatables data for active books."
    return datatables_source(False)


@bp.route("/archived", methods=["GET"])
def archived():
    "List archived books."
    language_choices = lute.utils.formutils.language_choices("(all languages)")
    current_language_id = lute.utils.formutils.valid_current_language_id()

    return render_template(
        "book/index.html",
        status="Archived",
        language_choices=language_choices,
        current_language_id=current_language_id,
    )


# Archived must be capitalized, or the ajax call 404's.
@bp.route("/datatables/Archived", methods=["POST"])
def datatables_archived_source():
    "Datatables data for archived books."
    return datatables_source(True)


def _book_from_url(url):
    "Create a new book, or flash an error if can't parse."
    b = Book()
    try:
        b = service.book_from_url(url)
    except service.BookImportException as e:
        flash(e.message, "notice")
        b = Book()
    return b


def _language_is_rtl_map():
    """
    Return language-id to is_rtl map, to be used during book creation.
    """
    ret = {}
    for lang in db.session.query(Language).all():
        ret[lang.id] = lang.right_to_left
    return ret


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
            book = repo.add(b)
            repo.commit()
            return redirect(f"/read/{book.id}/page/1", 302)
        except service.BookImportException as e:
            flash(e.message, "notice")

    # Don't set the current language before submit.
    current_language_id = int(UserSetting.get_value("current_language_id"))
    form.language_id.data = current_language_id

    return render_template(
        "book/create_new.html",
        book=b,
        form=form,
        tags=repo.get_book_tags(),
        rtl_map=json.dumps(_language_is_rtl_map()),
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
        repo.add(b)
        repo.commit()
        flash(f"{b.title} updated.")
        return redirect("/", 302)

    lang = Language.find(b.language_id)
    return render_template(
        "book/edit.html",
        book=b,
        title_direction="rtl" if lang.right_to_left else "ltr",
        form=form,
        tags=repo.get_book_tags(),
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
