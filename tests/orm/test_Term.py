"""
Term mapping tests.
"""

import pytest
from lute.models.term import Term, TermTag, TermTextChangedException
from lute.db import db
from tests.dbasserts import assert_sql_result


def test_save_and_remove(empty_db, english):
    "Smoke test of mappings and db records."
    sql = "select WoText, WoTextLC, WoTokenCount from words"
    assert_sql_result(sql, [], "empty table")

    term = Term(english, "ABC")

    db.session.add(term)
    db.session.commit()
    assert_sql_result(sql, ["ABC; abc; 1"], "have term")

    db.session.delete(term)
    db.session.commit()
    assert_sql_result(sql, [], "no terms")


def test_term_with_parent_and_tags(empty_db, spanish):
    "Misc data check - parent and tags are saved."
    term = Term(spanish, "HOLA")
    parent = Term(spanish, "PARENT")
    term.add_parent(parent)

    tg = TermTag("tag")
    term.add_term_tag(tg)

    db.session.add(term)
    db.session.commit()

    sql = "select WoID, WoText, WoTextLC from words"
    expected = ["1; HOLA; hola", "2; PARENT; parent"]
    assert_sql_result(sql, expected, "sanity check on save")

    assert_sql_result("select WpWoID, WpParentWoID from wordparents", ["1; 2"], "wp")

    # Hacky sql check.
    sql = """select w.WoText, p.WoText as ptext, tags.TgText
        FROM words w
        INNER JOIN wordparents on WpWoID = w.WoID
        INNER JOIN words p on p.WoID = wordparents.WpParentWoID
        INNER JOIN wordtags on WtWoID = w.WoID
        INNER JOIN tags on TgID = WtTgID"""
    exp = ["HOLA; PARENT; tag"]
    assert_sql_result(sql, exp, "parents, tags")


def test_term_parent_with_two_children(spanish):
    "Both children get saved in the db."
    term = Term(spanish, "HOLA")
    gato = Term(spanish, "gato")
    parent = Term(spanish, "PARENT")
    gato.add_parent(parent)
    term.add_parent(parent)

    db.session.add(term)
    db.session.add(gato)
    db.session.commit()

    parent_get = Term.find(parent.id)
    assert parent_get.text == "PARENT"
    assert len(parent_get.children) == 2

    expected = [f"{term.id}; {parent.id}", f"{gato.id}; {parent.id}"]
    expected.sort()
    sql = """select WpWoID, WpParentWoID
    from wordparents order by WpWoID"""
    assert_sql_result(sql, expected, "wp")


def test_add_and_remove_parents(spanish):
    "Parent mappings."
    term = Term(spanish, "HOLA")
    p1 = Term(spanish, "parent")
    p2 = Term(spanish, "otro")
    term.add_parent(p1)
    term.add_parent(p2)

    db.session.add(term)
    db.session.commit()

    sql = """select WpWoID, WpParentWoID
    from wordparents order by WpWoID, WpParentWoID"""

    expected = [
        f"{term.id}; {p1.id}",
        f"{term.id}; {p2.id}",
    ]
    expected.sort()
    assert_sql_result(sql, expected, "after change")

    term.remove_all_parents()
    db.session.add(term)
    db.session.commit()
    assert_sql_result(sql, [], "all removed")


def test_remove_parent_leaves_children_in_db(spanish):
    "Child deletion doesn't delete the parent."
    term = Term(spanish, "HOLA")
    parent = Term(spanish, "PARENT")
    term.add_parent(parent)

    db.session.add(term)
    db.session.commit()
    sql_list = "select WoText from words order by WoText"
    sql = f"""select w.WoText, p.WoText as ptext from words w
    left join wordparents on WpWoID = w.WoID
    left join words p on p.WoID = wordparents.WpParentWoID
    where w.WoID = {term.id}"""
    assert_sql_result(sql_list, ["HOLA", "PARENT"], "both exist")
    assert_sql_result(sql, ["HOLA; PARENT"], "parent set")

    db.session.delete(parent)
    db.session.commit()
    assert_sql_result(sql_list, ["HOLA"], "parent removed")
    assert_sql_result(sql, ["HOLA; None"], "parent not set")


def test_removing_term_with_parent_and_tag(empty_db, spanish):
    """
    Both the parent and the tag are left.
    """
    term = Term(spanish, "HOLA")
    parent = Term(spanish, "PARENT")
    term.add_parent(parent)
    tg = TermTag("tag")
    term.add_term_tag(tg)

    db.session.add(term)
    db.session.commit()
    sqllist = "select WoText from words order by WoText"
    sqltags = "select TgText from tags"
    assert_sql_result(sqllist, ["HOLA", "PARENT"], "both exist")
    assert_sql_result(sqltags, ["tag"], "tag exists")

    db.session.delete(term)
    db.session.commit()
    assert_sql_result(sqllist, ["PARENT"], "parent left")
    assert_sql_result(sqltags, ["tag"], "tag left")


def test_save_replace_remove_image(spanish):
    "Save saves the associated image."
    t = Term(spanish, "HOLA")
    t.set_current_image("hello.png")
    assert t.get_current_image() == "hello.png"

    db.session.add(t)
    db.session.commit()
    sql = "select WiWoID, WiSource from wordimages"
    expected = ["1; hello.png"]
    assert_sql_result(sql, expected, "hello")

    t.set_current_image("there.png")
    assert t.get_current_image() == "there.png"

    db.session.add(t)
    db.session.commit()
    expected = ["1; there.png"]
    assert_sql_result(sql, expected, "there")

    t.set_current_image(None)
    assert t.get_current_image() is None

    db.session.add(t)
    db.session.commit()
    expected = []
    assert_sql_result(sql, expected, "removed")


def test_delete_term_deletes_image(spanish):
    "Check cascade delete."
    t = Term(spanish, "HOLA")
    t.set_current_image("hello.png")
    assert t.get_current_image() == "hello.png"

    db.session.add(t)
    db.session.commit()
    sql = "select WiWoID, WiSource from wordimages"
    expected = ["1; hello.png"]
    assert_sql_result(sql, expected, "hello")

    db.session.delete(t)
    db.session.commit()
    assert_sql_result(sql, [], "removed")


def test_save_remove_flash_message(spanish):
    "Flash message is associated with term, can be popped."
    t = Term(spanish, "HOLA")
    t.set_flash_message("hello")
    assert t.get_flash_message() == "hello"

    db.session.add(t)
    db.session.commit()
    sql = "select WfWoID, WfMessage from wordflashmessages"
    expected = ["1; hello"]
    assert_sql_result(sql, expected, "hello")

    assert t.pop_flash_message() == "hello", "popped"
    assert t.get_flash_message() is None, "no message now"

    db.session.add(t)
    db.session.commit()
    assert_sql_result(sql, [], "popped")


def test_delete_term_deletes_flash_message(spanish):
    "Check cascade delete."
    t = Term(spanish, "HOLA")
    t.set_flash_message("hello")

    db.session.add(t)
    db.session.commit()
    sql = "select WfWoID, WfMessage from wordflashmessages"
    expected = ["1; hello"]
    assert_sql_result(sql, expected, "hello")

    db.session.delete(t)
    db.session.commit()
    assert_sql_result(sql, [], "popped")


## Changing term text isn't allowed -- changing case is ok.


@pytest.mark.term_case
def test_changing_text_of_saved_Term_throws(english):
    "Changing text should throw."
    term = Term(english, "ABC")
    db.session.add(term)
    db.session.commit()

    with pytest.raises(TermTextChangedException):
        term.text = "DEF"


@pytest.mark.term_case
def test_changing_text_to_same_thing_does_not_throw(japanese):
    """
    New terms get created on page open, and when parsed
    in full context of the text, the term may be parsed differently
    than when the form is opened.

    e.g. for Japanese, the term "集めれ" may get created on
    page load due to the term getting parsed in the full page context,
    but when parsed individually it's parsed as "集め/れ".
    Setting a new term with original text "集めれ" to that _same_ text
    means that the text is really _unchanged_.
    """
    term = Term.create_term_no_parsing(japanese, "集めれ")
    db.session.add(term)
    db.session.commit()

    sql = f"select wotext, wotextlc from words where woid = {term.id}"
    assert_sql_result(sql, ["集めれ; 集めれ"], "have term")

    t = Term.find(term.id)
    t.text = "集めれ"
    db.session.add(t)
    db.session.commit()
    assert_sql_result(sql, ["集めれ; 集めれ"], "have term")


@pytest.mark.term_case
def test_changing_multiword_text_case_does_not_throw(english):
    """
    Sanity check.
    """
    term = Term(english, "a CAT")
    db.session.add(term)
    db.session.commit()

    sql = f"select wotext, wotextlc from words where woid = {term.id}"
    assert_sql_result(sql, ["a/ /CAT; a/ /cat"], "have term")

    t = Term.find(term.id)
    t.text = term.text.lower()
    db.session.add(t)
    db.session.commit()
    assert_sql_result(sql, ["a/ /cat; a/ /cat"], "have term")


@pytest.mark.term_case
def test_changing_case_only_of_text_of_saved_Term_is_ok(english):
    "Changing text should throw."
    term = Term(english, "ABC")
    db.session.add(term)
    db.session.commit()

    term.text = "abc"


@pytest.mark.term_case
def test_changing_text_of_non_saved_Term_is_ok(english):
    "Changing text should not throw if not saved."
    term = Term(english, "ABC")
    term.text = "DEF"
