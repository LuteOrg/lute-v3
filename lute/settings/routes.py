"""
Settings routes.
"""

import os
from flask import (
    Blueprint,
    request,
    Response,
    render_template,
    redirect,
    flash,
    jsonify,
)
from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SelectField, IntegerField, TextAreaField
from wtforms.validators import InputRequired, NumberRange
from wtforms import ValidationError
from lute.config.app_config import AppConfig
from lute.models.language import Language
from lute.models.setting import UserSetting
from lute.db import db
from lute.parse.mecab_parser import JapaneseParser


class UserSettingsForm(FlaskForm):
    """
    Settings.

    Note the field names here must match the keys in the settings table.
    """

    backup_enabled = SelectField(
        "Backup Enabled", choices=[("-", "(not set)"), ("y", "yes"), ("n", "no")]
    )
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

    custom_styles = TextAreaField("Custom styles")

    mecab_path = StringField("MECAB_PATH environment variable")

    def validate_backup_enabled(self, field):
        "User should acknowledge."
        if field.data == "-":
            raise ValidationError('Please change "Backup enabled" to either yes or no.')

    def validate_backup_dir(self, field):
        "Field must be set if enabled."
        if self.backup_enabled.data != "y":
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

    ac = AppConfig.create_from_config()
    if ac.is_docker:
        # User shouldn't change some things with docker.
        kw = {"readonly": True, "style": "background-color: LightGray"}
        form.backup_dir.render_kw = kw
        form.mecab_path.render_kw = kw

    if form.validate_on_submit():
        # Update the settings in the database
        for field in form:
            if field.id not in ("csrf_token", "submit"):
                UserSetting.set_value(field.id, field.data)
        db.session.commit()

        JapaneseParser.set_mecab_path_envkey(form.mecab_path.data)

        flash("Settings updated", "success")
        return redirect("/")

    # Load current settings from the database
    for field in form:
        if field.id != "csrf_token":
            field.data = UserSetting.get_value(field.id)
    # Hack: set boolean settings to ints, otherwise they're always checked.
    form.backup_warn.data = int(form.backup_warn.data or 0)
    form.backup_auto.data = int(form.backup_auto.data or 0)

    return render_template("settings/form.html", form=form)


@bp.route("/test_mecab", methods=["GET"])
def test_parse():
    """
    Do a test parse for the JapaneseParser using the
    given path string.

    Returns { 'success': tokens }, or { 'error' msg }

    """
    mecab_path = request.args.get("mecab_path", None)
    old_key = JapaneseParser.get_mecab_path_envkey()
    result = {"failure": "tbd"}
    try:
        JapaneseParser.set_mecab_path_envkey(mecab_path)
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
        JapaneseParser.set_mecab_path_envkey(old_key)

    return jsonify(result)


@bp.route("/custom_styles", methods=["GET"])
def custom_styles():
    """
    Return the custom settings for inclusion in the base.html.
    """
    css = UserSetting.get_value("custom_styles")
    response = Response(css, 200)
    response.content_type = "text/css; charset=utf-8"
    return response
