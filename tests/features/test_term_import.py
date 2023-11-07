"""
Step defs for term_import.feature.
"""
# pylint: disable=missing-function-docstring

import os
import tempfile
import pytest

from pytest_bdd import given, then, scenarios, parsers

from lute.models.language import Language
from lute.models.term import Term

from lute.termimport.service import import_file, BadImportFileError

from tests.dbasserts import assert_sql_result


# The content of the file for the current test.
content = None

scenarios("term_import.feature")


@given("demo data")
def given_demo_data(app_context):
    "Calling app_context loads the demo data."


@given(parsers.parse("import file:\n{newcontent}"))
def given_file(newcontent):
    global content  # pylint: disable=global-statement
    content = newcontent


@given("empty import file")
def given_empty_file():
    global content  # pylint: disable=global-statement
    content = ""


@then(parsers.parse("import should succeed with {created} created, {skipped} skipped"))
def succeed_with_status(created, skipped):
    fd, path = tempfile.mkstemp()
    with os.fdopen(fd, "w") as tmp:
        # do stuff with temp file
        tmp.write(content)

    stats = import_file(path)
    os.remove(path)

    assert stats["created"] == int(created), "created"
    assert stats["skipped"] == int(skipped), "skipped"


@then(parsers.parse("import should fail with message:\n{message}"))
def fail_with_message(message):
    fd, path = tempfile.mkstemp()
    with os.fdopen(fd, "w") as tmp:
        # do stuff with temp file
        tmp.write(content)
    with pytest.raises(BadImportFileError, match=message):
        import_file(path)
    os.remove(path)


@then(parsers.parse("words table should contain:\n{text_lc_content}"))
def then_words_table_contains_WoTextLC(text_lc_content):
    expected = text_lc_content.split("\n")
    sql = "select WoTextLC from words order by WoTextLC"
    assert_sql_result(sql, expected)


@then(parsers.parse('{language} term "{term}" should be:\n{expected}'))
def then_term_tags(language, term, expected):
    lang = Language.find_by_name(language)
    spec = Term(lang, term)
    t = Term.find_by_spec(spec)
    pstring = ", ".join([p.text for p in t.parents])
    if pstring == "":
        pstring = "-"
    tstring = ", ".join([p.text for p in t.term_tags])
    if tstring == "":
        tstring = "-"
    actual = [
        f"translation: {t.translation or '-'}",
        f"pronunciation: {t.romanization or '-'}",
        f"status: {t.status}",
        f"parents: {pstring}",
        f"tags: {tstring}",
    ]
    assert "\n".join(actual) == expected, "term"


@then(parsers.parse('sql "{sql}" should return:\n{expected}'))
def then_sql_returns(sql, expected):
    expected = expected.split("\n")
    assert_sql_result(sql, expected)
