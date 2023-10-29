"""
Backup routes.

Backup settings form management, and running backups.
"""

import os
from flask import Blueprint, render_template, redirect, flash
from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SelectField, IntegerField
from wtforms.validators import InputRequired, NumberRange
from wtforms import ValidationError
from lute.models.setting import Setting
from lute.db import db


class BackupSettingsForm(FlaskForm):
    """
    Backup settings.

    Note the field names here must match the keys in the settings table.
    """

    backup_enabled = SelectField(
        'Backup Enabled',
        choices = [
            ('-', '(not set)'),
            ('y', 'yes'),
            ('n', 'no')
        ]
    )
    backup_dir = StringField('Backup Directory')
    backup_auto = BooleanField('Run Backups Automatically (Daily)')
    backup_warn = BooleanField('Warn If Backup Hasn\'t Run in a Week')
    backup_count = IntegerField('Backup Count', validators=[InputRequired(), NumberRange(min=1)])

    def validate_backup_enabled(self, field):
        "User should acknowledge."
        if field.data == '-':
            raise ValidationError('Please change "Backup enabled" to either yes or no.')

    def validate_backup_dir(self, field):
        "Field must be set if enabled."
        if self.backup_enabled.data != 'y':
            return
        v = field.data
        if (v or '').strip() == '':
            raise ValidationError('Backup directory required')

        abspath = os.path.abspath(v)
        if v != abspath:
            msg = f'Backup dir must be absolute path.  Did you mean "{abspath}"?'
            raise ValidationError(msg)
        if not os.path.exists(v):
            raise ValidationError(f'Directory "{v}" does not exist.')
        if not os.path.isdir(v):
            raise ValidationError(f'"{v}" is not a directory.')


bp = Blueprint('backup', __name__, url_prefix='/backup')

@bp.route('/settings', methods=['GET', 'POST'])
def backup_settings():
    "Edit backup settings."
    form = BackupSettingsForm()
    if form.validate_on_submit():
        # Update the settings in the database
        for field in form:
            if field.id not in ('csrf_token', 'submit'):
                Setting.set_value(field.id, field.data)
        db.session.commit()
        flash('Backup settings updated', 'success')
        return redirect('/')

    # Load current settings from the database
    for field in form:
        if field.id != 'csrf_token':
            field.data = Setting.get_value(field.id)
    # Hack: set boolean settings to ints, otherwise they're always checked.
    form.backup_warn.data = int(form.backup_warn.data)
    form.backup_auto.data = int(form.backup_auto.data)

    return render_template('backup/settings.html', form=form)
