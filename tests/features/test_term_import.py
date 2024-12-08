"""
Step defs for term_import.feature.
"""
# pylint: disable=missing-function-docstring

import os
import tempfile
import pytest

from pytest_bdd import given, when, then, scenarios, parsers

from lute.db import db
from lute.models.language import Language
from lute.language.service import Service as LanguageService
from lute.models.term import Term
from lute.models.repositories import LanguageRepository, TermRepository
from lute.termimport.service import Service, BadImportFileError

from tests.dbasserts import assert_sql_result


# The content of the file for the current test.
content = None

# The results of the import
stats = None

scenarios("term_import.feature")
scenarios("term_import_status_0.feature")


@given("demo data")
def given_demo_data(app_context):
    "Load languages necessary for imports."
    svc = LanguageService(db.session)
    for lang in ["Spanish", "English", "Classical Chinese"]:
        svc.load_language_def(lang)


@given(parsers.parse("import file:\n{newcontent}"))
def given_file(newcontent):
    global content  # pylint: disable=global-statement
    content = newcontent


@given("empty import file")
def given_empty_file():
    global content  # pylint: disable=global-statement
    content = ""


@when(parsers.parse("import with create {create}, update {update}"))
def import_with_settings(create, update):
    fd, path = tempfile.mkstemp()
    with os.fdopen(fd, "w") as tmp:
        # do stuff with temp file
        tmp.write(content)

    global stats  # pylint: disable=global-statement
    service = Service(db.session)
    stats = service.import_file(
        path, create.lower() == "true", update.lower() == "true"
    )
    os.remove(path)


@when(
    parsers.parse(
        "import with create {create}, update {update}, new as unknown {newunknowns}"
    )
)
def import_with_settings_and_newunks(create, update, newunknowns):
    fd, path = tempfile.mkstemp()
    with os.fdopen(fd, "w") as tmp:
        # do stuff with temp file
        tmp.write(content)

    global stats  # pylint: disable=global-statement
    service = Service(db.session)
    stats = service.import_file(
        path,
        create.lower() == "true",
        update.lower() == "true",
        newunknowns.lower() == "true",
    )
    os.remove(path)


@then(
    parsers.parse(
        "import should succeed with {created} created, {updated} updated, {skipped} skipped"
    )
)
def succeed_with_status(created, updated, skipped):
    assert stats["created"] == int(created), "created"
    assert stats["updated"] == int(updated), "updated"
    assert stats["skipped"] == int(skipped), "skipped"


@then(parsers.parse("import should fail with message:\n{message}"))
def fail_with_message(message):
    fd, path = tempfile.mkstemp()
    with os.fdopen(fd, "w") as tmp:
        # do stuff with temp file
        tmp.write(content)
    with pytest.raises(BadImportFileError, match=message):
        service = Service(db.session)
        service.import_file(path)
    os.remove(path)


@then(parsers.parse("words table should contain:\n{text_lc_content}"))
def then_words_table_contains_WoTextLC(text_lc_content):
    expected = []
    if text_lc_content != "-":
        expected = text_lc_content.split("\n")
    sql = "select WoTextLC from words order by WoTextLC"
    assert_sql_result(sql, expected)


@then(parsers.parse('{language} term "{term}" should be:\n{expected}'))
def then_term_tags(language, term, expected):
    repo = LanguageRepository(db.session)
    lang = repo.find_by_name(language)
    spec = Term(lang, term)
    term_repo = TermRepository(db.session)
    t = term_repo.find_by_spec(spec)
    pstring = ", ".join([p.text for p in t.parents])
    if pstring == "":
        pstring = "-"
    tstring = ", ".join(sorted([p.text for p in t.term_tags]))
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
