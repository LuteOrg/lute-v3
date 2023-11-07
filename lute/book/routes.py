"""
/book routes.
"""

import requests
from bs4 import BeautifulSoup

from flask import Blueprint, request, jsonify, render_template, redirect, flash
from lute.utils.data_tables import DataTablesFlaskParamParser
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


@bp.route("/new", methods=["GET", "POST"])
def new():
    "Create a new book, either from text or from a file."
    b = Book()
    form = NewBookForm(obj=b)
    form.language_id.choices = lute.utils.formutils.language_choices()
    repo = Repository(db)

    if form.validate_on_submit():
        form.populate_obj(b)
        if form.textfile.data:
            content = form.textfile.data.read()
            b.text = str(content, "utf-8")
        book = repo.add(b)
        repo.commit()
        return redirect(f"/read/{book.id}/page/1", 302)

    parameters = request.args
    import_url = parameters.get("importurl", "").strip()
    if import_url != "":
        b = load_book(import_url)
        form = NewBookForm(obj=b)
        form.language_id.choices = lute.utils.formutils.language_choices()

    return render_template(
        "book/create_new.html",
        book=b,
        form=form,
        tags=repo.get_book_tags(),
        show_language_selector=True,
    )


def load_book(url):
    "Parse the url and load a new Book."
    s = None
    try:
        timeout = 20  # seconds
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        s = response.text
    except requests.exceptions.RequestException as e:
        msg = f"Could not parse {url} (error: {str(e)})"
        flash(msg, "notice")
        return Book()

    soup = BeautifulSoup(s, "html.parser")
    extracted_text = []

    # Add elements in order found.
    for element in soup.descendants:
        if element.name in ("h1", "h2", "h3", "h4", "p"):
            extracted_text.append(element.text)

    title_node = soup.find("title")
    orig_title = title_node.string if title_node else url

    short_title = orig_title[:150]
    if len(orig_title) > 150:
        short_title += " ..."

    b = Book()
    b.title = short_title
    b.source_uri = url
    b.text = "\n\n".join(extracted_text)
    return b


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
