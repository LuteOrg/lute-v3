"""
Book create/edit forms.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, FieldList, TextAreaField, FileField
from wtforms import ValidationError
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileRequired, FileAllowed

from lute.models.language import Language
from lute.models.book import Book


class NewBookForm(FlaskForm):
    """
    New book.  All fields can be entered.
    """

    language_id = SelectField(
        'Language',
        coerce=int
    )

    title = StringField('Title', validators=[DataRequired(), Length(max=255)])
    text = TextAreaField('Text', description='Use for short texts, e.g. up to a few thousand words. For longer texts, use the "Text File" below.')
    textfile = FileField('Text file', description='Max file size 2048K', validators=[FileAllowed(['txt'], 'Please upload a valid text document')])
    source_uri = StringField('Source URI', validators=[Length(max=255)])
    book_tags = FieldList(StringField('book_tags'))

    def validate_language_id(self, field): # pylint: disable=unused-argument
        "Language must be set."
        if self.language_id.data in (None, 0):
            raise ValidationError("Please select a language")

    def validate_text(self, field): # pylint: disable=unused-argument
        "Throw if missing text and textfile, or if have both."
        have_text = self.text.data not in ('', None)
        have_textfile = self.textfile.data not in ('', None)
        if have_text and have_textfile:
            raise ValidationError("Both Text and Text file are set, please only specify one")
        if have_text is False and have_textfile is False:
            raise ValidationError("Please specify either Text or Text file")
