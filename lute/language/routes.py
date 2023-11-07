"""
/language endpoints.
"""

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from flask import Blueprint, current_app, render_template, redirect, url_for, flash
from lute.models.language import Language
from lute.models.book import Book
from lute.models.term import Term
from lute.language.forms import LanguageForm
from lute.db import db
from lute.db.demo import predefined_languages

bp = Blueprint("language", __name__, url_prefix="/language")


@bp.route("/index")
def index():
    """
    List all languages.

    This includes the Book and Term count for each Language.  These
    counts are pulled in by subqueries, because Language doesn't have
    "books" and "terms" members ... I was having trouble with session
    management when these were added, and they're only used here, so
    this is good enough for now.
    """

    def create_count_subquery(class_, count_column):
        # Re the pylint disable, ref
        # https://github.com/pylint-dev/pylint/issues/8138 ...
        ret = (
            db.session.query(
                class_.language_id,
                # pylint: disable=not-callable
                func.count(class_.id).label(count_column),
            )
            .group_by(class_.language_id)
            .subquery()
        )
        return ret

    # Create subqueries for counting books and terms
    book_subquery = create_count_subquery(Book, "book_count")
    term_subquery = create_count_subquery(Term, "term_count")

    # Query to join Language with book and term counts
    query = (
        db.session.query(
            Language, book_subquery.c.book_count, term_subquery.c.term_count
        )
        .outerjoin(book_subquery, Language.id == book_subquery.c.language_id)
        .outerjoin(term_subquery, Language.id == term_subquery.c.language_id)
    )

    results = query.all()

    results = [rec for rec in results if rec[0].is_supported is True]

    return render_template("language/index.html", language_data=results)


def _handle_form(language, form) -> bool:
    """
    Handle the language form processing.

    Returns True if validated and saved.
    """
    result = False

    if form.validate_on_submit():
        try:
            form.populate_obj(language)
            current_app.db.session.add(language)
            current_app.db.session.commit()
            flash(f"Language {language.name} updated", "success")
            result = True
        except IntegrityError as e:
            msg = e.orig
            if "languages.LgName" in f"{e.orig}":
                msg = f"{language.name} already exists."
            flash(msg, "error")

    return result


@bp.route("/edit/<int:langid>", methods=["GET", "POST"])
def edit(langid):
    """
    Edit a language.
    """
    language = db.session.get(Language, langid)

    if not language:
        flash(f"Language {langid} not found", "danger")
        return redirect(url_for("language.index"))

    form = LanguageForm(obj=language)
    if _handle_form(language, form):
        return redirect("/")
    return render_template("language/edit.html", form=form, language=language)


@bp.route("/new", defaults={"langname": None}, methods=["GET", "POST"])
@bp.route("/new/<string:langname>", methods=["GET", "POST"])
def new(langname):
    """
    Create a new language.
    """
    predefined = predefined_languages()
    language = Language()
    if langname is not None:
        candidates = [lang for lang in predefined if lang.name == langname]
        if len(candidates) == 1:
            language = candidates[0]

    form = LanguageForm(obj=language)
    if _handle_form(language, form):
        return redirect("/")

    return render_template(
        "language/new.html", form=form, language=language, predefined=predefined
    )


@bp.route("/delete/<int:langid>", methods=["POST"])
def delete(langid):
    """
    Delete a language.
    """
    language = db.session.get(Language, langid)
    if not language:
        flash(f"Language {langid} not found")
    Language.delete(language)
    return redirect(url_for("language.index"))
