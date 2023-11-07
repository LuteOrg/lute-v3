"""
Forms while reading.
"""

from flask_wtf import FlaskForm
from wtforms import TextAreaField


class TextForm(FlaskForm):
    """
    Text page - for editing a page.
    """

    text = TextAreaField("Text")
