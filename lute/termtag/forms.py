"""
Flask-wtf forms.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, ValidationError
from wtforms.validators import DataRequired

from lute.db import db
from lute.models.repositories import TermTagRepository

DUPLICATE_TAG_MSG = (
    "Tag already exists. To move terms onto it, use bulk edit on the Terms "
    "page (/term/index): add the existing tag and remove this one, then "
    "delete the unused tag."
)


class TermTagForm(FlaskForm):
    """
    TermTag.
    """

    text = StringField("Tag", validators=[DataRequired()])
    comment = TextAreaField("Comment")

    def __init__(self, *args, **kwargs):
        "Remember the tag being edited so its own name still validates."
        # Read obj before FlaskForm binds request.form. Passing formdata=None
        # would skip that binding.
        termtag = kwargs.get("obj")
        self.termtag_id = None if termtag is None else termtag.id
        super().__init__(*args, **kwargs)

    def validate_text(self, field):
        "Tag text must not match another tag."
        repo = TermTagRepository(db.session)
        existing = repo.find_by_text(field.data)
        if existing is not None and existing.id != self.termtag_id:
            raise ValidationError(DUPLICATE_TAG_MSG)
