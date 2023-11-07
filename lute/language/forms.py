"""
Flask-wtf forms.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SelectField
from wtforms.validators import DataRequired
from lute.parse.registry import supported_parsers


class LanguageForm(FlaskForm):
    """
    Language.
    """

    name = StringField("Name", validators=[DataRequired()])
    dict_1_uri = StringField("Dictionary 1", validators=[DataRequired()])
    dict_2_uri = StringField("Dictionary 2")
    sentence_translate_uri = StringField(
        "Sentence translation", validators=[DataRequired()]
    )
    show_romanization = BooleanField("Show Romanization field")
    right_to_left = BooleanField("Right-to-left")

    parser_type = SelectField("Parse as", choices=supported_parsers().items())
    character_substitutions = StringField("Character substitutions")

    regexp_split_sentences = StringField(
        "Split sentences at", validators=[DataRequired()]
    )
    exceptions_split_sentences = StringField("Split sentence exceptions")
    word_characters = StringField("Word characters", validators=[DataRequired()])
