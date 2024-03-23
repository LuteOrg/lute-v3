"""
Term tests.
"""

import datetime
import pytest
from sqlalchemy import text
from lute.models.term import Term, TermImage
from lute.db import db
from tests.dbasserts import assert_record_count_equals, assert_sql_result


def test_cruft_stripped_on_set_word(spanish):
    "Extra spaces are stripped, because they cause parsing/matching problems."
    cases = [
        ("hola", "hola", "hola"),
        ("    hola    ", "hola", "hola"),
        # This case should never occur:
        # tabs are stripped out of text, and returns mark different sentences.
        # ('   hola\tGATO\nok', 'hola GATO ok', 'hola gato ok'),
    ]

    for s, expected_text, expected_text_lc in cases:
        term = Term(spanish, s)
        assert term.text == expected_text
        assert term.text_lc == expected_text_lc


def test_token_count(english):
    "Various scenarios."
    cases = [
        ("hola", 1),
        ("    hola    ", 1),
        ("  hola  gato", 3),
        ("HOLA hay\tgato  ", 5),
        ("  the CAT's pyjamas  ", 7),
        # This only has 9 tokens, because the "'" is included with
        # the following space ("' ").
        ("A big CHUNK O' stuff", 9),
        ("YOU'RE", 3),
        ("...", 1),  # should never happen :-)
    ]

    for s, expected_token_count in cases:
        term = Term(english, s)
        assert term.token_count == expected_token_count


def test_term_left_as_is_if_its_an_exception(spanish):
    "Ensure regex match works, upper and lowercase."
    spanish.exceptions_split_sentences = "EE.UU."

    term = Term(spanish, "EE.UU.")
    assert term.token_count == 1
    assert term.text == "EE.UU."

    term = Term(spanish, "ee.uu.")
    assert term.token_count == 1
    assert term.text == "ee.uu."


def test_cannot_add_self_as_own_parent(spanish):
    "Avoid circular references."
    t = Term(spanish, "gato")
    t.add_parent(t)
    assert len(t.parents) == 0

    otherterm = Term(spanish, "gato")
    t.add_parent(otherterm)
    assert len(t.parents) == 0, "different object still not added"


def test_find_by_spec(app_context, spanish, english):
    """
    Can find by spec, matches on language and text.
    """
    t = Term(spanish, "gato")
    db.session.add(t)
    db.session.commit()

    spec = Term(spanish, "GATO")
    found = Term.find_by_spec(spec)
    assert found.id == t.id, "term found by matching spec"

    spec = Term(english, "GATO")
    found = Term.find_by_spec(spec)
    assert found is None, "not found in different language"

    spec = Term(spanish, "gatito")
    found = Term.find_by_spec(spec)
    assert found is None, "not found with different text"


# WoStatusChanged checks.
#
# Saving a term changes WoStatusChanged date, via a db trigger.


@pytest.fixture(name="_saved_term")
def fixture_saved_term(app_context, english):
    "Saved term."
    t = Term(english, "hello")
    db.session.add(t)
    db.session.commit()
    return t


def _get_field_value(_saved_term):
    "Get the updated date, and the timestamp."
    sql = text(
        """
        SELECT
          WoStatusChanged,
          ROUND((JULIANDAY(datetime('now')) - JULIANDAY(WoStatusChanged)) * 86400) as diffsecs
        FROM words
        WHERE WoID = :term_id
    """
    )

    result = db.session.execute(sql, {"term_id": _saved_term.id}).fetchone()
    diff = int(result[1])
    return [result[0], diff]


def _assert_updated(_saved_term):
    "Assert the status field was updated."
    val, diff = _get_field_value(_saved_term)
    msg = f"Was updated (set to {val})"
    assert diff <= 100, msg


@pytest.mark.term_status_change
def test_set_on_save_new(app_context, _saved_term):
    "On save of new Term, status changed is creation date."
    _assert_updated(_saved_term)

    sql = "select * from words where WoCreated != WoStatusChanged"
    assert_record_count_equals(sql, 0, "status changed matches created date")


@pytest.mark.term_status_change
def test_update_status_updates_date(app_context, _saved_term):
    "On update, if status has changed, change date."
    db.session.execute(text('update words set WoStatusChanged = "2000-01-01 12:00:00"'))
    db.session.commit()
    sql = 'select * from words where WoStatusChanged = "2000-01-01 12:00:00"'
    assert_record_count_equals(sql, 1, "WoStatusChanged set to test value")

    _saved_term.status = 2
    db.session.add(_saved_term)
    db.session.commit()
    _assert_updated(_saved_term)

    assert_record_count_equals(sql, 0, "updated")


@pytest.mark.term_status_change
def test_saving_with_unchanged_status_leaves_date(app_context, _saved_term):
    "On update, if status has not changed, don't change date."
    db.session.execute(text('update words set WoStatusChanged = "2000-01-01 12:00:00"'))
    db.session.commit()
    _saved_term.status = _saved_term.status
    db.session.add(_saved_term)
    db.session.commit()
    sql = 'select * from words where WoStatusChanged = "2000-01-01 12:00:00"'
    assert_record_count_equals(sql, 1, "WoStatusChanged not updated")


@pytest.mark.term_status_change
def test_update_status_via_sql_updates_date(app_context, _saved_term):
    "On update, if status has changed, change date."
    db.session.execute(text('update words set WoStatusChanged = "2000-01-01 12:00:00"'))
    db.session.commit()
    sql = 'select * from words where WoStatusChanged = "2000-01-01 12:00:00"'
    assert_record_count_equals(sql, 1, "WoStatusChanged set to test value")

    db.session.execute(text("update words set WoStatus = 1"))
    db.session.commit()
    assert_record_count_equals(sql, 1, "same status = same WoStatusChanged")

    db.session.execute(text("update words set WoStatus = 2"))
    db.session.commit()
    assert_record_count_equals(sql, 0, "updated WoStatusChanged")


def test_save_new_image_all_existing_images_replaced(app_context, spanish):
    "All existing terms removed."
    t = Term(spanish, "hola")
    ti1 = TermImage()
    ti1.term = t
    ti1.source = "1.png"
    t.images.append(ti1)

    ti2 = TermImage()
    ti2.term = t
    ti2.source = "2.png"
    t.images.append(ti2)
    db.session.add(t)
    db.session.commit()

    assert_record_count_equals("select * from wordimages", 2, "image count")

    t.set_current_image("3.png")
    db.session.add(t)
    db.session.commit()
    assert_record_count_equals("select * from wordimages", 1, "new image count")
    assert_record_count_equals(
        "select * from wordimages where wisource='3.png'", 1, "new image count"
    )


def test_delete_empty_image_records(app_context, spanish):
    "Check cleanup."
    t = Term(spanish, "hola")
    for s in ["", "   ", "3.png"]:
        ti = TermImage()
        ti.term = t
        ti.source = s
        t.images.append(ti)
    db.session.add(t)
    db.session.commit()

    assert_sql_result("select wisource from wordimages", ["", "   ", "3.png"], "images")

    Term.delete_empty_images()
    assert_sql_result("select wisource from wordimages", ["3.png"], "cleaned images")


def test_changing_status_of_status_0_term_resets_WoCreated(app_context, spanish):
    """
    New unknown Terms get created with Status = 0 when a page is
    rendered for reading, but that's not _really_ the date that the
    term was created.
    """
    t = Term(spanish, "hola")
    t.translation = "hi"
    t.status = 0
    db.session.add(t)
    db.session.commit()

    db.session.execute(text("update words set WoCreated = 'a'"))
    db.session.commit()
    sql = "select WoTranslation, WoCreated from words where WoCreated = 'a'"
    assert_sql_result(sql, ["hi; a"], "created date")

    t.status = 0
    t.translation = "hello"
    db.session.add(t)
    db.session.commit()
    assert_sql_result(sql, ["hello; a"], "created date still old value")

    t.status = 1
    t.translation = "howdy"
    db.session.add(t)
    db.session.commit()

    assert_sql_result(sql, [], "updated")
    current_year = str(datetime.datetime.now().year)
    sql_updated = "select strftime('%Y', WoCreated) from words"
    assert_sql_result(sql_updated, [f"{current_year}"], "final")
