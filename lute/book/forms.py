"""
Book create/edit forms.
"""

from wtforms import StringField, SelectField, FieldList, TextAreaField
from wtforms import ValidationError
from wtforms.validators import DataRequired, Length
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed


class NewBookForm(FlaskForm):
    """
    New book.  All fields can be entered.
    """

    language_id = SelectField("Language", coerce=int)

    title = StringField("Title", validators=[DataRequired(), Length(max=255)])

    desc = (
        "Use for short texts, e.g. up to a few thousand words. "
        + 'For longer texts, use the "Text File" below.'
    )
    text = TextAreaField("Text", description=desc)
    textfile = FileField(
        "Text file",
        description="Max file size 2048K",
        validators=[FileAllowed(["txt"], "Please upload a valid text document")],
    )
    source_uri = StringField("Text source", validators=[Length(max=255)])
    audiofile = FileField(
        "Audio file",
        validators=[
            FileAllowed(
                ["mp3", "wav", "ogg"],
                "Please upload a valid audio file (mp3, wav, ogg)",
            )
        ],
    )
    book_tags = FieldList(StringField("book_tags"))

    def validate_language_id(self, field):  # pylint: disable=unused-argument
        "Language must be set."
        if self.language_id.data in (None, 0):
            raise ValidationError("Please select a language")

    def validate_text(self, field):  # pylint: disable=unused-argument
        "Throw if missing text and textfile, or if have both."
        have_text = self.text.data not in ("", None)
        have_textfile = self.textfile.data not in ("", None)
        if have_text and have_textfile:
            raise ValidationError(
                "Both Text and Text file are set, please only specify one"
            )
        if have_text is False and have_textfile is False:
            raise ValidationError("Please specify either Text or Text file")


class EditBookForm(FlaskForm):
    """
    Edit existing book.  Only a few fields can be changed.
    """

    title = StringField("Title", validators=[DataRequired(), Length(max=255)])
    source_uri = StringField("Source URI", validators=[Length(max=255)])
    book_tags = FieldList(StringField("book_tags"))
    audiofile = FileField(
        "Audio file",
        validators=[
            FileAllowed(
                ["mp3", "wav", "ogg"],
                "Please upload a valid audio file (mp3, wav, ogg)",
            )
        ],
    )
