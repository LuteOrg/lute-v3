"""
Flask-wtf forms.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, FieldList, RadioField, TextAreaField, HiddenField
from wtforms import ValidationError
from wtforms.validators import DataRequired

from lute.models.language import Language
from lute.models.term import Term


class TermTagForm(FlaskForm):
    """
    TermTag.
    """

    text = StringField('Tag', validators=[DataRequired()])
    comment = TextAreaField('Comment')
