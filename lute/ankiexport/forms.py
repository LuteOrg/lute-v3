"""
SrsExportSpec form.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, Length
from lute.ankiexport.service import Service
from lute.models.srsexport import SrsExportSpec


class SrsExportSpecForm(FlaskForm):
    "Srs export spec."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Flask doesn't allow for "general" errors, so handle those
        # specially.
        self.general_errors = []

        # Extra data added to the form during POST
        # to simplify validation.
        self.anki_deck_names = None
        self.anki_note_types = None

    export_name = StringField(
        "Export Name", validators=[DataRequired(), Length(max=200)]
    )
    criteria = TextAreaField(
        "Criteria", render_kw={"placeholder": "Leave blank to always export"}
    )
    deck_name = SelectField("Deck Name", validators=[DataRequired(), Length(max=200)])
    note_type = SelectField("Note Type", validators=[DataRequired(), Length(max=200)])
    field_mapping = HiddenField(
        "Field Mapping", validators=[DataRequired(), Length(max=1000)]
    )
    active = BooleanField("Active", default=True)

    def validate(self, extra_validators=None):
        """Custom validation logic."""
        if not super().validate(extra_validators):
            return False  # Return early if standard validation fails

        temp_spec = SrsExportSpec()
        self.populate_obj(temp_spec)
        svc = Service(self.anki_deck_names, self.anki_note_types, [temp_spec])
        self.general_errors = svc.validate_spec(temp_spec)
        if len(self.general_errors) > 0:
            return False

        return True
