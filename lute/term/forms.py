"""
Flask-wtf forms.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, FieldList, RadioField, TextAreaField, HiddenField
from wtforms.validators import DataRequired


class TermForm(FlaskForm):
    """
    Term.
    """

    # TODO term form: language - use predefined
    language_id = SelectField(
        'Language',
        choices=[
            (3, 'English'),
        ])

    original_text = HiddenField('OriginalText')
    text = StringField('Text', validators=[DataRequired()], render_kw={"placeholder": "Term"})
    parents = FieldList(StringField('parent'))
    translation = TextAreaField('Translation', render_kw={"placeholder": "Translation"})
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

    current_image = HiddenField('current_image')
