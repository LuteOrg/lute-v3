"""
Settings routes.
"""

from flask import (
    Blueprint,
    current_app,
    request,
    render_template,
    redirect,
    flash,
    jsonify,
)
from wtforms import BooleanField
from lute.models.language import Language
from lute.models.setting import UserSetting
from lute.models.repositories import UserSettingRepository
from lute.themes.service import Service as ThemeService
from lute.settings.forms import UserSettingsForm, UserShortcutsForm
from lute.settings.current import refresh_global_settings
from lute.db import db
from lute.parse.mecab_parser import JapaneseParser


bp = Blueprint("settings", __name__, url_prefix="/settings")


@bp.route("/index", methods=["GET", "POST"])
def edit_settings():
    "Edit settings."
    form = UserSettingsForm()

    with current_app.app_context():
        svc = ThemeService(db.session)
        form.current_theme.choices = svc.list_themes()

    ac = current_app.env_config
    if ac.is_docker:
        # User shouldn't change some things with docker.
        kw = {"readonly": True, "style": "background-color: LightGray"}
        # Backup dir gets mounted from host.
        form.backup_dir.render_kw = kw

    repo = UserSettingRepository(db.session)
    if form.validate_on_submit():
        # Update the settings in the database
        for field in form:
            if field.id not in ("csrf_token", "submit"):
                repo.set_value(field.id, field.data)
        db.session.commit()
        refresh_global_settings(db.session)

        flash("Settings updated", "success")
        return redirect("/")

    # Load current settings from the database
    for field in form:
        if field.id != "csrf_token":
            field.data = repo.get_value(field.id)
        if isinstance(field, BooleanField):
            # Hack: set boolean settings to ints, otherwise they're always checked.
            field.data = int(field.data or 0)

    return render_template("settings/form.html", form=form)


@bp.route("/test_mecab", methods=["GET"])
def test_parse():
    """
    Do a test parse for the JapaneseParser using the
    given path string.

    Returns { 'success': tokens }, or { 'error' msg }

    """
    mecab_path = request.args.get("mecab_path", None)
    repo = UserSettingRepository(db.session)
    old_setting = repo.get_value("mecab_path")
    result = {"failure": "tbd"}
    try:
        repo.set_value("mecab_path", mecab_path)
        # Parsing requires a language, even if it's a dummy.
        lang = Language()
        p = JapaneseParser()
        src = "私は元気です"
        toks = p.get_parsed_tokens(src, lang)
        toks = [tok.token for tok in toks if tok.token != "¶"]
        message = f"{src} parsed to [{ ', '.join(toks) }]"
        result = {"result": "success", "message": message}
    except Exception as e:  # pylint: disable=broad-exception-caught
        message = f"{type(e).__name__}: { str(e) }"
        result = {"result": "failure", "message": message}
    finally:
        repo.set_value("mecab_path", old_setting)

    return jsonify(result)


@bp.route("/set/<key>/<value>", methods=["POST"])
def set_key_value(key, value):
    "Set a UserSetting key to value."
    repo = UserSettingRepository(db.session)
    old_value = repo.get_value(key)
    try:
        repo.set_value(key, value)
        result = {"result": "success", "message": "OK"}
    except Exception as e:  # pylint: disable=broad-exception-caught
        message = f"{type(e).__name__}: { str(e) }"
        repo.set_value(key, old_value)
        result = {"result": "failure", "message": message}
    db.session.commit()
    refresh_global_settings(db.session)
    return jsonify(result)


def _get_categorized_hotkeys():
    """
    Return hotkey UserSetting keys and values,
    grouped by category.
    """

    categorized_settings = {
        "Navigation": [
            "hotkey_StartHover",
            "hotkey_PrevWord",
            "hotkey_NextWord",
            "hotkey_PrevUnknownWord",
            "hotkey_NextUnknownWord",
            "hotkey_PrevSentence",
            "hotkey_NextSentence",
        ],
        "Update status": [
            "hotkey_Status1",
            "hotkey_Status2",
            "hotkey_Status3",
            "hotkey_Status4",
            "hotkey_Status5",
            "hotkey_StatusIgnore",
            "hotkey_StatusWellKnown",
            "hotkey_StatusUp",
            "hotkey_StatusDown",
            "hotkey_DeleteTerm",
        ],
        "Translate": [
            "hotkey_TranslateSentence",
            "hotkey_TranslatePara",
            "hotkey_TranslatePage",
        ],
        "Copy": [
            "hotkey_CopySentence",
            "hotkey_CopyPara",
            "hotkey_CopyPage",
        ],
        "Misc": [
            "hotkey_Bookmark",
            "hotkey_EditPage",
            "hotkey_NextTheme",
            "hotkey_ToggleHighlight",
            "hotkey_ToggleFocus",
            "hotkey_SaveTerm",
        ],
    }

    settings = {h.key: h.value for h in db.session.query(UserSetting).all()}
    return {
        category: {k: settings[k] for k in keylist}
        for category, keylist in categorized_settings.items()
    }


@bp.route("/shortcuts", methods=["GET", "POST"])
def edit_shortcuts():
    "Edit shortcuts."
    repo = UserSettingRepository(db.session)
    form = UserShortcutsForm()
    if form.validate_on_submit():
        # print(request.form, flush=True)
        # Update the settings in the database
        for k, v in request.form.items():
            # print(f"{k} = {v}", flush=True)
            repo.set_value(k, v)
        db.session.commit()
        refresh_global_settings(db.session)
        flash("Shortcuts updated", "success")
        return redirect("/")

    categorized_settings = _get_categorized_hotkeys()

    setting_descs = {
        "hotkey_StartHover": "Deselect all words",
        "hotkey_PrevWord": "Move to previous word",
        "hotkey_NextWord": "Move to next word",
        "hotkey_PrevUnknownWord": "Move to previous unknown word",
        "hotkey_NextUnknownWord": "Move to next unknown word",
        "hotkey_PrevSentence": "Move to previous sentence",
        "hotkey_NextSentence": "Move to next sentence",
        "hotkey_StatusUp": "Bump the status up by 1",
        "hotkey_StatusDown": "Bump that status down by 1",
        "hotkey_Bookmark": "Bookmark the current page",
        "hotkey_CopySentence": "Copy the sentence of the current word",
        "hotkey_CopyPara": "Copy the paragraph of the current word",
        "hotkey_CopyPage": "Copy the full page",
        "hotkey_TranslateSentence": "Translate the sentence of the current word",
        "hotkey_TranslatePara": "Translate the paragraph of the current word",
        "hotkey_TranslatePage": "Translate the full page",
        "hotkey_NextTheme": "Change to the next theme",
        "hotkey_ToggleHighlight": "Toggle highlights",
        "hotkey_ToggleFocus": "Toggle focus mode",
        "hotkey_Status1": "Set status to 1",
        "hotkey_Status2": "Set status to 2",
        "hotkey_Status3": "Set status to 3",
        "hotkey_Status4": "Set status to 4",
        "hotkey_Status5": "Set status to 5",
        "hotkey_StatusIgnore": "Set status to Ignore",
        "hotkey_StatusWellKnown": "Set status to Well Known",
        "hotkey_DeleteTerm": "Delete term (set status to Unknown)",
        "hotkey_EditPage": "Edit the current page",
        "hotkey_SaveTerm": "Save term in term form",
    }

    return render_template(
        "settings/shortcuts.html",
        setting_descs=setting_descs,
        categorized_settings=categorized_settings,
    )
