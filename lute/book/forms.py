"""
Book create/edit forms.
"""

import os
import json
from flask import request, flash
from wtforms import StringField, SelectField, TextAreaField, IntegerField, HiddenField
from wtforms import ValidationError
from wtforms.validators import DataRequired, Length, NumberRange
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from lute.book import service


def _get_file_content(filefielddata):
    """
    Get the content of the file.
    """
    _, ext = os.path.splitext(filefielddata.filename)
    ext = (ext or "").lower()
    if ext == ".txt":
        return service.get_textfile_content(filefielddata)
    if ext == ".epub":
        return service.get_epub_content(filefielddata)
    if ext == ".pdf":
        msg = """
        Note: pdf imports can be inaccurate, due to how PDFs are encoded.
        Please be aware of this while reading.
        """
        flash(msg, "notice")
        return service.get_pdf_content_from_form(filefielddata)
    if ext == ".srt":
        return service.get_srt_content(filefielddata)
    if ext == ".vtt":
        return service.get_vtt_content(filefielddata)
    raise ValueError(f'Unknown file extension "{ext}"')


class NewBookForm(FlaskForm):
    """
    New book.  All fields can be entered.
    """

    language_id = SelectField("Language", coerce=int)

    title = StringField("Title", validators=[DataRequired(), Length(max=255)])

    desc = (
        "Use for short texts, e.g. up to a few thousand words. "
        + 'For longer texts, use the "Text file" below.'
    )
    text = TextAreaField("Text", description=desc)
    textfile = FileField(
        "Text file",
        validators=[
            FileAllowed(
                ["txt", "epub", "pdf", "srt", "vtt"],
                "Please upload a valid '.txt', '.epub', '.pdf', '.srt' or '.vtt' file.",
            )
        ],
    )
    max_page_tokens = IntegerField(
        "Words per page",
        validators=[NumberRange(min=10, max=1500)],
        default=250,
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
    book_tags = StringField("Tags")

    def __init__(self, *args, **kwargs):
        "Call the constructor of the superclass (FlaskForm)"
        super().__init__(*args, **kwargs)
        book = kwargs.get("obj")

        def _data(arr):
            "Get data in proper format for tagify."
            return json.dumps([{"value": p} for p in arr])

        self.book_tags.data = _data(book.book_tags)
        if request.method == "POST":
            self.book_tags.data = request.form.get("book_tags", "")

    def populate_obj(self, obj):
        "Call the populate_obj method from the parent class, then mine."
        super().populate_obj(obj)

        def _values(field_data):
            "Convert field data to array."
            ret = []
            if field_data:
                ret = [h["value"] for h in json.loads(field_data)]
            return ret

        obj.book_tags = _values(self.book_tags.data)

        if self.textfile.data:
            obj.text = _get_file_content(self.textfile.data)
        f = self.audiofile.data
        if f:
            obj.audio_filename = service.save_audio_file(f)

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
    book_tags = StringField("Tags")
    audiofile = FileField(
        "Audio file",
        validators=[
            FileAllowed(
                ["mp3", "wav", "ogg"],
                "Please upload a valid audio file (mp3, wav, ogg)",
            )
        ],
    )

    # The current audio_filename can be removed from the current book.
    audio_filename = HiddenField("Audio filename")

    def __init__(self, *args, **kwargs):
        "Call the constructor of the superclass (FlaskForm)"
        super().__init__(*args, **kwargs)
        book = kwargs.get("obj")

        def _data(arr):
            "Get data in proper format for tagify."
            return json.dumps([{"value": p} for p in arr])

        self.book_tags.data = _data(book.book_tags)
        if request.method == "POST":
            self.book_tags.data = request.form.get("book_tags", "")

    def populate_obj(self, obj):
        "Call the populate_obj method from the parent class, then mine."
        super().populate_obj(obj)

        def _values(field_data):
            "Convert field data to array."
            ret = []
            if field_data:
                ret = [h["value"] for h in json.loads(field_data)]
            return ret

        obj.book_tags = _values(self.book_tags.data)

        f = self.audiofile.data
        if f:
            obj.audio_filename = service.save_audio_file(f)
            obj.audio_bookmarks = None
            obj.audio_current_pos = None
