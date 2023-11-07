"""
Flask-wtf forms.
"""

from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SelectField,
    FieldList,
    RadioField,
    TextAreaField,
    HiddenField,
)
from wtforms import ValidationError
from wtforms.validators import DataRequired

from lute.models.language import Language
from lute.models.term import Term


class TermForm(FlaskForm):
    """
    Term.
    """

    language_id = SelectField("Language", coerce=int)

    original_text = HiddenField("OriginalText")
    text = StringField(
        "Text", validators=[DataRequired()], render_kw={"placeholder": "Term"}
    )
    parents = FieldList(StringField("parent"))
    translation = TextAreaField("Translation", render_kw={"placeholder": "Translation"})
    romanization = StringField(
        "Romanization", render_kw={"placeholder": "Pronunciation"}
    )

    status_choices = [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (99, "Wkn"), (98, "Ign")]
    status = RadioField("Status", choices=status_choices)

    term_tags = FieldList(StringField("term_tags"))

    current_image = HiddenField("current_image")

    def validate_language_id(self, field):  # pylint: disable=unused-argument
        "Language must be set."
        if self.language_id.data in (None, 0):
            raise ValidationError("Please select a language")

    def validate_text(self, field):  # pylint: disable=unused-argument
        "Throw if form text changes from the original or is a dup."
        # Don't continue if the language isn't set.
        if self.language_id.data in (None, 0):
            return
        langid = int(self.language_id.data)
        lang = Language.find(langid)
        if lang is None:
            return

        if self.original_text.data in ("", None):
            # New term.
            spec = Term(lang, self.text.data)
            checkdup = Term.find_by_spec(spec)
            if checkdup is None:
                # Not a dup.
                return
            # Is a dup.
            raise ValidationError("Term already exists")

        if self.text.data == self.original_text.data:
            return
        langid = int(self.language_id.data)
        newterm = Term(lang, self.text.data)
        origterm = Term(lang, self.original_text.data)
        if newterm.text_lc != origterm.text_lc:
            raise ValidationError("Can only change term case")
