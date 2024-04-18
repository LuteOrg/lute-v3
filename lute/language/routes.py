"""
/language endpoints.
"""

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from flask import Blueprint, current_app, render_template, redirect, url_for, flash
from lute.models.language import Language
from lute.models.setting import UserSetting
from lute.models.book import Book
from lute.models.term import Term
import lute.language.service
from lute.language.forms import LanguageForm
from lute.db import db
from lute.parse.registry import supported_parsers

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


def _add_hidden_dictionary_template_entry(form):
    "Add a dummy placeholder dictionary to be used as a template."
    # Add a dummy dictionary entry with dicturi __TEMPLATE__.
    #
    # This entry is used as a "template" when adding a new dictionary
    # to the list of dictionaries (see templates/language/_form.html).
    # This is the easiest way to ensure that new dictionary entries
    # have the correct controls.
    #
    # This dummy entry is not rendered on the form, or submitted
    # when the form is submitted.  Search for __TEMPLATE__ in
    # templates/language/_form.html to see where it is handled.
    form.dictionaries.append_entry({"dicturi": "__TEMPLATE__"})


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
    form.parser_type.choices = supported_parsers()

    if _handle_form(language, form):
        return redirect("/")

    _add_hidden_dictionary_template_entry(form)

    return render_template("language/edit.html", form=form, language=language)


@bp.route("/new", defaults={"langname": None}, methods=["GET", "POST"])
@bp.route("/new/<string:langname>", methods=["GET", "POST"])
def new(langname):
    """
    Create a new language.
    """
    predefined = lute.language.service.predefined_languages()
    language = Language()
    if langname is not None:
        candidates = [lang for lang in predefined if lang.name == langname]
        if len(candidates) == 1:
            language = candidates[0]

    form = LanguageForm(obj=language)
    form.parser_type.choices = supported_parsers()

    if _handle_form(language, form):
        # New language, so show everything b/c user should re-choose
        # the default.
        #
        # Reason for this: a user may start off with just language X,
        # so the current_language_id is set to X.id.  If the user then
        # adds language Y, the filter stays on X, which may be
        # disconcerting/confusing.  Forcing a reselect is painless and
        # unambiguous.
        UserSetting.set_value("current_language_id", 0)
        db.session.commit()
        return redirect("/")

    _add_hidden_dictionary_template_entry(form)

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


@bp.route("/list_predefined", methods=["GET"])
def list_predefined():
    "Show predefined languages that are not already in the db."
    predefined = lute.language.service.predefined_languages()
    existing_langs = db.session.query(Language).all()
    existing_names = [l.name for l in existing_langs]
    new_langs = [p for p in predefined if p.name not in existing_names]
    return render_template("language/list_predefined.html", predefined=new_langs)


@bp.route("/load_predefined/<langname>", methods=["GET"])
def load_predefined(langname):
    "Load a predefined language and its stories."
    lang_id = lute.language.service.load_language_def(langname)
    UserSetting.set_value("current_language_id", lang_id)
    db.session.commit()
    flash(f"Loaded {langname} and sample book(s)")
    return redirect("/")
