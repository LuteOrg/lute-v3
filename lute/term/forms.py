"""
Flask-wtf forms.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SelectField
from wtforms.validators import DataRequired


class TermForm(FlaskForm):
    """
    Term.
    """
    text = StringField('Text', validators=[DataRequired()])
