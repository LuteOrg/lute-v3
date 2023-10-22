"""
Flask-wtf forms.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, FieldList, RadioField  #, HiddenField
from wtforms.validators import DataRequired


class TermForm(FlaskForm):
    """
    Term.
    """

    # TODO term form: add fields

    # TODO term form: language - use predefined
    language_id = SelectField(
        'Language',
        choices=[
            (3, 'English'),
        ])

    # TODO term form: hide this, change to HiddenField
    original_text = StringField('OriginalText')
    text = StringField('Text', validators=[DataRequired()], render_kw={"placeholder": "Term"})
    parents = FieldList(StringField('parent'))
    translation = StringField('Translation', render_kw={"placeholder": "Translation"})
    romanization = StringField('Romanization', render_kw={"placeholder": "Pronunciation"})

    status_choices = [
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (99, 'Wkn'),
        (98, 'Ign')
    ]
    status = RadioField('Status', choices=status_choices)

    term_tags = FieldList(StringField('term_tags'))
    # TODO term form: hide this, change to HiddenField
    current_image = StringField('OriginalText')
