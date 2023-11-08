"""
DataTables sqlite tests.
"""

from lute.utils.formutils import language_choices


def test_language_choices(app_context):
    "Gets all languages."
    choices = language_choices()
    assert choices[0][1] == "-", "- at the top"
    langnames = [c[1] for c in choices]
    assert "Spanish" in langnames, "have Spanish"
