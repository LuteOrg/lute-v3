"""
Flask-wtf forms.
"""

from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    IntegerField,
    BooleanField,
    SelectField,
    FormField,
    FieldList,
    Form,
    ValidationError,
)
from wtforms.validators import DataRequired
from lute.models.language import LanguageDictionary


class LanguageDictionaryForm(Form):
    """
    Language dictionary form, nested in Language form.
    """

    usefor = SelectField(
        choices=[("terms", "Terms"), ("sentences", "Sentences")],
        render_kw={"title": "Use dictionary for"},
    )
    dicttype = SelectField(
        choices=[
            ("embeddedhtml", "Embedded"),
            ("popuphtml", "Pop-up window"),
        ],
        render_kw={"title": "Show as"},
    )
    dicturi = StringField("URL", validators=[DataRequired()])
    is_active = BooleanField("Is active", render_kw={"title": "Is active?"})
    sort_order = IntegerField("Sort", render_kw={"style": "display: none"})

    def validate_dicturi(self, field):  # pylint: disable=unused-argument
        "Language must be set."
        # TODO TERM_for_dict_lookup_key: re-add <TERM> criteria.
        #  and "<TERM>" not in field.data:
        if "###" not in field.data:
            raise ValidationError("Dictionary URI must contain ###")  # or <TERM>


class LanguageForm(FlaskForm):
    """
    Language.
    """

    name = StringField("Name", validators=[DataRequired()])
    dictionaries = FieldList(
        FormField(LanguageDictionaryForm, default=LanguageDictionary)
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
        "Split sentences at (default: all Unicode sentence terminators)"
    )
    exceptions_split_sentences = StringField("Split sentence exceptions")
    word_characters = StringField(
        "Word characters (default: all Unicode letters and marks)"
    )

    def validate_dictionaries(self, field):  # pylint: disable=unused-argument
        "Dictionaries must be valid."

        # raise ValueError(self.dictionaries.data) # debugging
        def _get_actives(usefor):
            "Return dictionaries."
            return [
                d
                for d in self.dictionaries.data
                if d.get("usefor", "") == usefor and d.get("is_active")
            ]

        term_dicts = _get_actives("terms")
        sentence_dicts = _get_actives("sentences")
        if len(term_dicts) == 0:
            raise ValidationError("Please add an active Terms dictionary")
        if len(sentence_dicts) == 0:
            raise ValidationError("Please add an active Sentences dictionary")
