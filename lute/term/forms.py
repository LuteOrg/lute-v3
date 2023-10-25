"""
Flask-wtf forms.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, FieldList, RadioField, TextAreaField, HiddenField
from wtforms import ValidationError
from wtforms.validators import DataRequired

from lute.models.language import Language
from lute.models.term import Term
from lute.db import db


class TermForm(FlaskForm):
    """
    Term.
    """

    language_id = SelectField(
        'Language',
        coerce=int
    )

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


    def validate_language_id(form, field):
        "Language must be set."
        if form.language_id.data in (None, 0):
            raise ValidationError("Please select a language")


    def validate_text(form, field):
        "Throw if form text changes from the original or is a dup."
        # Don't continue if the language isn't set.
        if form.language_id.data in (None, 0):
            return
        langid = int(form.language_id.data)
        lang = Language.find(langid)
        if lang is None:
            return

        if form.original_text.data in ('', None):
            # New term.
            spec = Term(lang, form.text.data)
            checkdup = Term.find_by_spec(spec)
            if checkdup is None:
                # Not a dup.
                return
            # Is a dup.
            raise ValidationError("Term already exists")

        if form.text.data == form.original_text.data:
            return
        langid = int(form.language_id.data)
        newterm = Term(lang, form.text.data)
        origterm = Term(lang, form.original_text.data)
        if newterm.text_lc != origterm.text_lc:
            raise ValidationError("Can only change term case")

