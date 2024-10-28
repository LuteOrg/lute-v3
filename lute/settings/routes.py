"""
Settings routes.
"""

import os
from flask import (
    Blueprint,
    current_app,
    request,
    render_template,
    redirect,
    flash,
    jsonify,
)
from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, IntegerField, TextAreaField, SelectField
from wtforms.validators import InputRequired, NumberRange
from wtforms import ValidationError
from lute.models.language import Language
from lute.models.setting import UserSetting
from lute.themes.service import list_themes
from lute.db import db
from lute.parse.mecab_parser import JapaneseParser


class UserSettingsForm(FlaskForm):
    """
    Settings.

    Note the field names here must match the keys in the settings table.
    """

    backup_enabled = BooleanField("Backup Enabled")
    backup_dir = StringField("Backup directory")
    backup_auto = BooleanField("Run backups automatically (daily)")
    backup_warn = BooleanField("Warn if backup hasn't run in a week")
    backup_count = IntegerField(
        "Retain backup count",
        validators=[InputRequired(), NumberRange(min=1)],
        render_kw={
            "title": "Count of zipfiles to retain, oldest files are deleted first"
        },
    )

    current_theme = SelectField("Theme")
    custom_styles = TextAreaField("Custom styles")
    show_highlights = BooleanField("Highlight terms by status")

    open_popup_in_new_tab = BooleanField("Open popup in new tab")
    stop_audio_on_term_form_open = BooleanField("Stop audio on term form open")
    stats_calc_sample_size = IntegerField(
        "Book stats page sample size",
        validators=[InputRequired(), NumberRange(min=1, max=500)],
        render_kw={"title": "Number of pages to use for book stats calculation."},
    )

    mecab_path = StringField("MECAB_PATH environment variable")
    reading_choices = [
        ("katakana", "Katakana"),
        ("hiragana", "Hiragana"),
        ("alphabet", "Romaji"),
    ]
    japanese_reading = SelectField("Pronunciation characters", choices=reading_choices)

    def validate_backup_dir(self, field):
        "Field must be set if enabled."
        if self.backup_enabled.data is False:
            return
        v = field.data
        if (v or "").strip() == "":
            raise ValidationError("Backup directory required")

        abspath = os.path.abspath(v)
        if v != abspath:
            msg = f'Backup dir must be absolute path.  Did you mean "{abspath}"?'
            raise ValidationError(msg)
        if not os.path.exists(v):
            raise ValidationError(f'Directory "{v}" does not exist.')
        if not os.path.isdir(v):
            raise ValidationError(f'"{v}" is not a directory.')


bp = Blueprint("settings", __name__, url_prefix="/settings")


@bp.route("/index", methods=["GET", "POST"])
def edit_settings():
    "Edit settings."
    form = UserSettingsForm()

    with current_app.app_context():
        form.current_theme.choices = list_themes()

    ac = current_app.env_config
    if ac.is_docker:
        # User shouldn't change some things with docker.
        kw = {"readonly": True, "style": "background-color: LightGray"}
        # Backup dir gets mounted from host.
        form.backup_dir.render_kw = kw

    if form.validate_on_submit():
        # Update the settings in the database
        for field in form:
            if field.id not in ("csrf_token", "submit"):
                UserSetting.set_value(field.id, field.data)
        db.session.commit()

        flash("Settings updated", "success")
        return redirect("/")

    # Load current settings from the database
    for field in form:
        if field.id != "csrf_token":
            field.data = UserSetting.get_value(field.id)
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
    old_setting = UserSetting.get_value("mecab_path")
    result = {"failure": "tbd"}
    try:
        UserSetting.set_value("mecab_path", mecab_path)
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
        UserSetting.set_value("mecab_path", old_setting)

    return jsonify(result)


@bp.route("/set/<key>/<value>", methods=["POST"])
def set_key_value(key, value):
    "Set a UserSetting key to value."
    old_value = UserSetting.get_value(key)
    try:
        UserSetting.set_value(key, value)
        result = {"result": "success", "message": "OK"}
    except Exception as e:  # pylint: disable=broad-exception-caught
        message = f"{type(e).__name__}: { str(e) }"
        UserSetting.set_value(key, old_value)
        result = {"result": "failure", "message": message}
    db.session.commit()
    return jsonify(result)


class UserShortcutsForm(FlaskForm):
    """
    Shortcuts form.

    The route manages getting and storing the settings
    from the db, as there's a variable number of settings,
    and it's easier to just work with the data directly
    rather than trying to create a variable number of fields.

    I'm only using this form to get the validate_on_submit()!
    There's likely a better way to do this.
    """


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
    form = UserShortcutsForm()
    if form.validate_on_submit():
        # print(request.form, flush=True)
        # Update the settings in the database
        for k, v in request.form.items():
            # print(f"{k} = {v}", flush=True)
            UserSetting.set_value(k, v)
        db.session.commit()
        flash("Shortcuts updated", "success")
        return redirect("/")

    categorized_settings = _get_categorized_hotkeys()

    setting_descs = {
        "hotkey_StartHover": "Deselect all words",
        "hotkey_PrevWord": "Move to previous word",
        "hotkey_NextWord": "Move to next word",
        "hotkey_PrevUnknownWord": "Move to previous unknown word",
        "hotkey_NextUnknownWord": "Move to next unknown word",
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
    }

    return render_template(
        "settings/shortcuts.html",
        setting_descs=setting_descs,
        categorized_settings=categorized_settings,
    )
