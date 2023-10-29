"""
Backup routes.

Backup settings form management, and running backups.
"""

import os
from flask import Blueprint, render_template, redirect, url_for, flash
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

    def validate_backup_dir(self, field):
        "Field must be set if enabled."
        if self.backup_enabled != 'y':
            return
        if (self.backup_dir, '').strip() == '':
            raise ValidationError('Backup directory required')
        if not os.path.exists(self.backup_dir):
            raise ValidationError(f'{self.backup_dir} does not exist.')
        if not os.path.isdir(self.backup_dir):
            raise ValidationError(f'{self.backup_dir} is not a directory.')
        

bp = Blueprint('backup', __name__, url_prefix='/backup')

@bp.route('/settings', methods=['GET', 'POST'])
def backup_settings():
    "Edit backup settings."
    form = BackupSettingsForm()
    if form.validate_on_submit():
        # Update the settings in the database
        for field in form:
            if field.id != 'csrf_token' and field.id != 'submit':
                Setting.set_value(field.id, field.data)
        db.session.commit()
        flash('Backup settings updated', 'success')
        return redirect('/')
    
    # Load current settings from the database
    for field in form:
        if field.id != 'csrf_token' and field.id != 'submit':
            field.data = Setting.get_value(field.id)
    
    return render_template('backup/settings.html', form=form)
