"""
Step defs for term_parent_mapping.feature.
"""
# pylint: disable=missing-function-docstring

import os
import tempfile
import pytest

from pytest_bdd import given, then, scenarios, parsers

from lute.db import db
from lute.models.term import Term

from lute.term_parent_map.service import import_file, BadImportFileError

from tests.utils import add_terms
from tests.dbasserts import assert_sql_result


# The content of the file for the current test.
content = None

# The current language.
language = None

scenarios("term_parent_mapping.feature")


@given("demo data")
def given_demo_data(app_context):
    "Calling app_context loads the demo data."


@given("language Spanish")
def lang_spanish(spanish):
    "Do-nothing step, just for clarity."
    global language  # pylint: disable=global-statement
    language = spanish


@given(parsers.parse("terms:\n{terms}"))
def given_terms(terms):
    terms = terms.split("\n")
    add_terms(language, terms)


@given(parsers.parse("import file:\n{newcontent}"))
def given_file(newcontent):
    global content  # pylint: disable=global-statement
    content = newcontent


@given("empty import file")
def given_empty_file():
    global content  # pylint: disable=global-statement
    content = ""


@given(parsers.parse('"{parent}" is parent of "{child}"'))
def given_parent(parent, child):
    spec = Term(language, parent)
    p = Term.find_by_spec(spec)
    spec = Term(language, child)
    c = Term.find_by_spec(spec)
    c.parents.append(p)
    db.session.add(p)
    db.session.add(c)
    db.session.commit()


@then(parsers.parse("import should succeed with {created} created, {updated} updated"))
def succeed_with_status(created, updated):
    fd, path = tempfile.mkstemp()
    with os.fdopen(fd, "w") as tmp:
        # do stuff with temp file
        tmp.write(content)

    stats = import_file(language, path)
    os.remove(path)

    assert stats["created"] == int(created), "created"
    assert stats["updated"] == int(updated), "updated"


@then(parsers.parse("import should fail with message:\n{message}"))
def fail_with_message(message):
    fd, path = tempfile.mkstemp()
    with os.fdopen(fd, "w") as tmp:
        # do stuff with temp file
        tmp.write(content)
    with pytest.raises(BadImportFileError, match=message):
        import_file(language, path)
    os.remove(path)


@then(parsers.parse("words table should contain:\n{text_lc_content}"))
def then_words_table_contains_WoTextLC(text_lc_content):
    expected = []
    if text_lc_content != "-":
        expected = text_lc_content.split("\n")
    sql = "select WoTextLC from words order by WoTextLC"
    assert_sql_result(sql, expected)


@then(parsers.parse("parents should be:\n{expected}"))
def then_parents(expected):
    sql = """
    select p.WoTextLC, c.WoTextLC
    from words p
    inner join wordparents on WpParentWoID=p.WoID
    inner join words c on c.WoID = WpWoID
    order by p.WoTextLC, c.WoTextLC
    """
    if expected == "-":
        expected = []
    else:
        expected = expected.split("\n")
    assert_sql_result(sql, expected)


@then(parsers.parse('sql "{sql}" should return:\n{expected}'))
def then_sql_returns(sql, expected):
    expected = expected.split("\n")
    assert_sql_result(sql, expected)


@then(parsers.parse('"{txt}" flash message should be:\n{msg}'))
def then_flash(txt, msg):
    expected = None
    if msg != "-":
        expected = msg
    spec = Term(language, txt)
    t = Term.find_by_spec(spec)
    assert t.get_flash_message() == expected, "flash"
