"""
/language endpoints.
"""

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from flask import Blueprint, current_app, render_template, redirect, url_for, flash
from lute.models.language import Language
from lute.models.repositories import UserSettingRepository
from lute.language.service import Service
from lute.language.forms import LanguageForm
from lute.db import db
from lute.parse.registry import supported_parsers

bp = Blueprint("language", __name__, url_prefix="/language")


@bp.route("/index")
def index():
    """
    List all languages, with book and term counts.
    """

    # Using plain sql, easier to get bulk quantities.
    sql = """
    select LgID, LgName, LgIsActive, book_count, term_count from languages
    left outer join (
      select BkLgID, count(BkLgID) as book_count from books
      group by BkLgID
    ) bc on bc.BkLgID = LgID
    left outer join (
      select WoLgID, count(WoLgID) as term_count from words
      where WoStatus != 0
      group by WoLgID
    ) tc on tc.WoLgID = LgID
    order by LgName
    """
    result = db.session.execute(text(sql)).all()
    languages = [
        {
            "LgID": row[0],
            "LgName": row[1],
            "LgIsActive": bool(row[2]),
            "book_count": row[3],
            "term_count": row[4],
        }
        for row in result
    ]
    return render_template("language/index.html", language_data=languages)


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
            current_app.db.session.rollback()
            msg = e.orig
            if "languages.LgName" in f"{e.orig}":
                msg = f"Language {form.name.data} already exists."
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


def _dropdown_parser_choices():
    "Get dropdown list of parser type name to name."
    return [(a[0], a[1].name()) for a in supported_parsers()]


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
    form.parser_type.choices = _dropdown_parser_choices()

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
    service = Service(db.session)
    predefined = service.supported_predefined_languages()
    language = Language()
    if langname is not None:
        candidates = [lang for lang in predefined if lang.name == langname]
        if len(candidates) == 1:
            language = candidates[0]

    form = LanguageForm(obj=language)
    form.parser_type.choices = _dropdown_parser_choices()

    if _handle_form(language, form):
        # New language, so show everything b/c user should re-choose
        # the default.
        #
        # Reason for this: a user may start off with just language X,
        # so the current_language_id is set to X.id.  If the user then
        # adds language Y, the filter stays on X, which may be
        # disconcerting/confusing.  Forcing a reselect is painless and
        # unambiguous.
        repo = UserSettingRepository(db.session)
        repo.set_value("current_language_id", 0)
        db.session.commit()
        return redirect("/")

    _add_hidden_dictionary_template_entry(form)

    return render_template(
        "language/new.html", form=form, language=language, predefined=predefined
    )


@bp.route("/toggle_active/<int:langid>", methods=["POST"])
def toggle_active(langid):
    """
    Toggle a language's active (frozen/thawed) state.
    """
    language = db.session.get(Language, langid)
    if not language:
        flash(f"Language {langid} not found", "error")
        return redirect(url_for("language.index"))
    language.is_active = not language.is_active
    db.session.commit()
    if language.is_active:
        flash(f"Language '{language.name}' activated.", "success")
    else:
        flash(f"Language '{language.name}' frozen.", "info")
    return redirect(url_for("language.index"))


@bp.route("/delete/<int:langid>", methods=["POST"])
def delete(langid):
    """
    Delete a language.
    """
    language = db.session.get(Language, langid)
    if not language:
        flash(f"Language {langid} not found")
        return redirect(url_for("language.index"))
    try:
        db.session.delete(language)
        db.session.commit()
        flash(f"Language '{language.name}' deleted.", "success")
    except IntegrityError:
        db.session.rollback()
        flash(
            f"Cannot delete '{language.name}': it has associated books or terms. "
            "Remove them first, or freeze the language instead.",
            "error",
        )
    return redirect(url_for("language.index"))


@bp.route("/list_predefined", methods=["GET"])
def list_predefined():
    "Show supported predefined languages that are not already in the db."
    service = Service(db.session)
    predefined = service.supported_predefined_languages()
    existing_langs = db.session.query(Language).all()
    existing_names = [l.name for l in existing_langs]
    new_langs = [p for p in predefined if p.name not in existing_names]
    return render_template("language/list_predefined.html", predefined=new_langs)


@bp.route("/load_predefined/<langname>", methods=["GET"])
def load_predefined(langname):
    "Load a predefined language and its stories."
    service = Service(db.session)
    lang_id = service.load_language_def(langname)
    repo = UserSettingRepository(db.session)
    repo.set_value("current_language_id", lang_id)
    db.session.commit()
    flash(f"Loaded {langname} and sample book(s)")
    return redirect("/")
