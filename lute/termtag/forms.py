"""
Flask-wtf forms.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired


class TermTagForm(FlaskForm):
    """
    TermTag.
    """

    text = StringField("Tag", validators=[DataRequired()])
    comment = TextAreaField("Comment")
