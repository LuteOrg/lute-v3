"""
SrsExportSpec form.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length


class SrsExportSpecForm(FlaskForm):
    "Srs export spec."
    export_name = StringField(
        "Export Name", validators=[DataRequired(), Length(max=200)]
    )
    criteria = TextAreaField("Criteria", validators=[DataRequired(), Length(max=1000)])
    deck_name = StringField("Deck Name", validators=[DataRequired(), Length(max=200)])
    note_type = StringField("Note Type", validators=[DataRequired(), Length(max=200)])
    field_mapping = TextAreaField(
        "Field Mapping", validators=[DataRequired(), Length(max=1000)]
    )
    active = BooleanField("Active", default=True)
