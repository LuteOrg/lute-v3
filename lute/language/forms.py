"""
Flask-wtf forms.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SelectField
from wtforms.validators import DataRequired


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
    show_romanization = BooleanField("Show Pronunciation field")
    right_to_left = BooleanField("Right-to-left")

    # Note!  The choices have to be set in the routes!
    # I originally had "choices=lute.parse.registry.supported_parsers()",
    # but it never worked: the Japanese mecab parser was excluded.
    # Possible coder error, not sure, but setting the choices at
    # form creation time works.
    parser_type = SelectField("Parse as", choices=[("tbd", "tbd")])

    character_substitutions = StringField("Character substitutions")

    regexp_split_sentences = StringField(
        "Split sentences at", validators=[DataRequired()]
    )
    exceptions_split_sentences = StringField("Split sentence exceptions")
    word_characters = StringField("Word characters", validators=[DataRequired()])
