"""
Term Repository tests.

Tests lute.term.model.Term *domain* objects being saved
and retrieved from DB.
"""

import pytest

from lute.models.term import Term as DBTerm, TermTag
from lute.db import db
from tests.dbasserts import assert_sql_result
from lute.term.model import Term, Repository


@pytest.fixture(name='repo')
def fixture_repo():
    return Repository(db)

@pytest.fixture(name='hello_term')
def fixture_hello_term(english):
    """
    Term business object with some defaults,
    no tags or parents.
    """
    t = Term()
    t.language_id = english.id
    t.text = 'HELLO'
    t.current_image = 'hello.png'
    t.flash_message = 'hello flash'
    return t


def test_save_new(english, app_context, hello_term, repo):
    """
    Saving a simple Term object loads the database.
    """

    sql = "select WoText, WoTextLC, WoTokenCount from words"
    assert_sql_result(sql, [], 'empty table')

    repo.add(hello_term)
    assert_sql_result(sql, [], 'Still empty')

    repo.commit()
    assert_sql_result(sql, [ "HELLO; hello; 1" ], 'Saved')


def test_save_updates_existing(english, app_context, hello_term, repo):
    """
    Saving Term updates an existing term if the text and lang
    matches.
    """

    term = DBTerm(english, 'HELLO')
    db.session.add(term)
    db.session.commit()
    sql = "select WoID, WoText, WoStatus from words"
    assert_sql_result(sql, [f'{term.id}; HELLO; 1'], 'have term')

    hello_term.language_id = english.id
    hello_term.text = 'hello'
    hello_term.status = 5

    repo.add(hello_term)
    repo.commit()
    assert_sql_result(sql, [f'{term.id}; hello; 5'], 'have term, status changed')


def test_save_existing_replaces_tags(english, app_context, repo):
    """
    If the db has a term with tags, and the business term changes
    those, the existing tags are replaced.
    """
    dbterm = DBTerm(english, 'HELLO')
    dbterm.add_term_tag(TermTag('a'))
    dbterm.add_term_tag(TermTag('b'))
    db.session.add(dbterm)
    db.session.commit()
    sql = f"""select TgText from tags
    inner join wordtags on WtTgID = TgID
    where WtWoID = {dbterm.id}"""
    assert_sql_result(sql, [ 'a', 'b' ], 'have term tags')

    term = repo.find_by_id(dbterm.id)
    assert term.term_tags == [ 'a', 'b' ]

    term.term_tags = [ 'a', 'c' ]
    repo.add(term)
    repo.commit()
    assert_sql_result(sql, [ 'a', 'c' ], 'term tags changed')

    term.term_tags = []
    repo.add(term)
    repo.commit()
    assert_sql_result(sql, [], 'term tags removed')

    sql = "select TgText from tags order by TgText"
    assert_sql_result(sql, [ 'a', 'b', 'c' ], 'Source tags still exist')


def test_save_uses_existing_TermTags(english, app_context, repo, hello_term):
    "Don't create new TermTag records if they already exist."
    db.session.add(TermTag('a'))
    db.session.commit()

    sql = """select TgID, TgText, WoText
    from tags
    left join wordtags on WtTgID = TgID
    left join words on WoID = WtWoID
    order by TgText"""
    assert_sql_result(sql, [ '1; a; None' ], 'a tag exists')

    hello_term.term_tags = [ 'a', 'b' ]
    repo.add(hello_term)
    repo.commit()
    assert_sql_result(sql, [ '1; a; HELLO', '2; b; HELLO' ], 'a used, b created')


## Saving and parents.

def test_save_with_new_parent(app_context, repo, hello_term):
    """
    Given a Term with parents = [ 'newparent' ],
    new parent DBTerm is created, and is assigned translation and image and tag.
    """
    hello_term.parents = [ 'parent' ]
    hello_term.term_tags = [ 'a', 'b' ]
    repo.add(hello_term)
    repo.commit()
    assert_sql_result('select WoText from words', [ 'HELLO', 'parent' ], 'parent created')

    parent = repo.find_by_langid_and_text(hello_term.language_id, 'parent')
    assert isinstance(parent, Term), 'is a Term bus. object'
    assert parent.text == 'parent'
    assert parent.term_tags == hello_term.term_tags
    assert parent.term_tags == [ 'a', 'b' ]  # just spelling it out.
    assert parent.translation == hello_term.translation
    assert parent.current_image == hello_term.current_image
    assert parent.parents == []


## Find tests.

def test_find_by_id(empty_db, english, repo):
    "Smoke test."
    t = DBTerm(english, 'Hello')
    t.set_current_image('hello.png')
    t.add_term_tag(TermTag('a'))
    t.add_term_tag(TermTag('b'))
    db.session.add(t)
    db.session.commit()
    assert t.id is not None, 'ID assigned'

    term = repo.find_by_id(t.id)
    assert term.id == t.id
    assert term.language_id == english.id
    assert term.text == 'Hello'
    assert term.original_text == 'Hello'
    assert term.current_image == 'hello.png'
    assert len(term.parents) == 0
    assert term.term_tags == [ 'a', 'b' ]


def test_find_by_id_throws_if_bad_id(empty_db, english, repo):
    "If app says term id = 7 exists, and it doesn't, that's a problem."
    with pytest.raises(ValueError):
        repo.find_by_id(9876)


# def test_save_and_remove(empty_db, english):
#     "Smoke test of mappings and db records."
#     sql = "select WoText, WoTextLC, WoTokenCount from words"
#     assert_sql_result(sql, [], 'empty table')
# 
#     term = Term()
#     term.language = english
#     term.text = 'ABC'
# 
#     db.session.add(term)
#     db.session.commit()
#     assert_sql_result(sql, ['ABC; abc; 1'], 'have term')
# 
#     db.session.delete(term)
#     db.session.commit()
#     assert_sql_result(sql, [], 'no terms')
# 
# 
# def test_term_with_parent_and_tags(empty_db, spanish):
#     "Misc data check - parent and tags are saved."
#     term = Term(spanish, "HOLA")
#     parent = Term(spanish, "PARENT")
#     term.add_parent(parent)
# 
#     tg = TermTag('tag')
#     term.add_term_tag(tg)
# 
#     db.session.add(term)
#     db.session.commit()
# 
#     sql = "select WoID, WoText, WoTextLC from words"
#     expected = [ "1; HOLA; hola", "2; PARENT; parent" ]
#     assert_sql_result(sql, expected, "sanity check on save")
# 
#     assert_sql_result("select WpWoID, WpParentWoID from wordparents", [ '1; 2' ], 'wp')
# 
#     # Hacky sql check.
#     sql = """select w.WoText, p.WoText as ptext, tags.TgText
#         FROM words w
#         INNER JOIN wordparents on WpWoID = w.WoID
#         INNER JOIN words p on p.WoID = wordparents.WpParentWoID
#         INNER JOIN wordtags on WtWoID = w.WoID
#         INNER JOIN tags on TgID = WtTgID"""
#     exp = [ "HOLA; PARENT; tag" ]
#     assert_sql_result(sql, exp, "parents, tags")
# 
# 
# def test_term_parent_with_two_children(spanish):
#     "Both children get saved in the db."
#     term = Term(spanish, "HOLA")
#     gato = Term(spanish, "gato")
#     parent = Term(spanish, "PARENT")
#     gato.add_parent(parent)
#     term.add_parent(parent)
# 
#     db.session.add(term)
#     db.session.add(gato)
#     db.session.commit()
# 
#     parent_get = Term.find(parent.id)
#     assert parent_get.text == "PARENT"
#     assert len(parent_get.children) == 2
# 
#     expected = [
#         f"{term.id}; {parent.id}",
#         f"{gato.id}; {parent.id}"
#     ]
#     expected.sort()
#     sql = """select WpWoID, WpParentWoID
#     from wordparents order by WpWoID"""
#     assert_sql_result(sql, expected, 'wp')
# 
# 
# def test_add_and_remove_parents(spanish):
#     "Parent mappings."
#     term = Term(spanish, "HOLA")
#     p1 = Term(spanish, "parent")
#     p2 = Term(spanish, "otro")
#     term.add_parent(p1)
#     term.add_parent(p2)
# 
#     db.session.add(term)
#     db.session.commit()
# 
#     sql = """select WpWoID, WpParentWoID
#     from wordparents order by WpWoID, WpParentWoID"""
# 
#     expected = [
#         f"{term.id}; {p1.id}",
#         f"{term.id}; {p2.id}",
#     ]
#     expected.sort()
#     assert_sql_result(sql, expected, 'after change')
# 
#     term.remove_all_parents()
#     db.session.add(term)
#     db.session.commit()
#     assert_sql_result(sql, [], 'all removed')
# 
# 
# def test_remove_parent_leaves_children_in_db(spanish):
#     "Child deletion doesn't delete the parent."
#     term = Term(spanish, "HOLA")
#     parent = Term(spanish, "PARENT")
#     term.add_parent(parent)
# 
#     db.session.add(term)
#     db.session.commit()
#     sql_list = "select WoText from words order by WoText"
#     sql = f"""select w.WoText, p.WoText as ptext from words w
#     left join wordparents on WpWoID = w.WoID
#     left join words p on p.WoID = wordparents.WpParentWoID
#     where w.WoID = {term.id}"""
#     assert_sql_result(sql_list, [ "HOLA", "PARENT" ], "both exist")
#     assert_sql_result(sql, [ "HOLA; PARENT" ], "parent set")
# 
#     db.session.delete(parent)
#     db.session.commit()
#     assert_sql_result(sql_list, [ "HOLA" ], "parent removed")
#     assert_sql_result(sql, [ "HOLA; None" ], "parent not set")
# 
# 
# def test_removing_term_with_parent_and_tag(empty_db, spanish):
#     """
#     Both the parent and the tag are left.
#     """
#     term = Term(spanish, "HOLA")
#     parent = Term(spanish, "PARENT")
#     term.add_parent(parent)
#     tg = TermTag('tag')
#     term.add_term_tag(tg)
# 
#     db.session.add(term)
#     db.session.commit()
#     sqllist = "select WoText from words order by WoText"
#     sqltags = "select TgText from tags"
#     assert_sql_result(sqllist, [ "HOLA", "PARENT" ], "both exist")
#     assert_sql_result(sqltags, [ "tag" ], "tag exists")
# 
#     db.session.delete(term)
#     db.session.commit()
#     assert_sql_result(sqllist, [ "PARENT" ], "parent left")
#     assert_sql_result(sqltags, [ "tag" ], "tag left")
# 
# 
# def test_save_replace_remove_image(spanish):
#     "Save saves the associated image."
#     t = Term(spanish, "HOLA")
#     t.set_current_image('hello.png')
#     assert t.get_current_image() == 'hello.png'
# 
#     db.session.add(t)
#     db.session.commit()
#     sql = "select WiWoID, WiSource from wordimages"
#     expected = ["1; hello.png"]
#     assert_sql_result(sql, expected, "hello")
# 
#     t.set_current_image('there.png')
#     assert t.get_current_image() == 'there.png'
# 
#     db.session.add(t)
#     db.session.commit()
#     expected = ["1; there.png"]
#     assert_sql_result(sql, expected, "there")
# 
#     t.set_current_image(None)
#     assert t.get_current_image() is None
# 
#     db.session.add(t)
#     db.session.commit()
#     expected = []
#     assert_sql_result(sql, expected, "removed")
# 
# 
# def test_delete_term_deletes_image(spanish):
#     "Check cascade delete."
#     t = Term(spanish, "HOLA")
#     t.set_current_image('hello.png')
#     assert t.get_current_image() == 'hello.png'
# 
#     db.session.add(t)
#     db.session.commit()
#     sql = "select WiWoID, WiSource from wordimages"
#     expected = ["1; hello.png"]
#     assert_sql_result(sql, expected, "hello")
# 
#     db.session.delete(t)
#     db.session.commit()
#     assert_sql_result(sql, [], "removed")
# 
# 
# def test_save_remove_flash_message(spanish):
#     "Flash message is associated with term, can be popped."
#     t = Term(spanish, "HOLA")
#     t.set_flash_message('hello')
#     assert t.get_flash_message() == 'hello'
# 
#     db.session.add(t)
#     db.session.commit()
#     sql = "select WfWoID, WfMessage from wordflashmessages"
#     expected = ["1; hello"]
#     assert_sql_result(sql, expected, "hello")
# 
#     assert t.pop_flash_message() == 'hello', 'popped'
#     assert t.get_flash_message() is None, 'no message now'
# 
#     db.session.add(t)
#     db.session.commit()
#     assert_sql_result(sql, [], "popped")
# 
# 
# def test_delete_term_deletes_flash_message(spanish):
#     "Check cascade delete."
#     t = Term(spanish, "HOLA")
#     t.set_flash_message('hello')
# 
#     db.session.add(t)
#     db.session.commit()
#     sql = "select WfWoID, WfMessage from wordflashmessages"
#     expected = ["1; hello"]
#     assert_sql_result(sql, expected, "hello")
# 
#     db.session.delete(t)
#     db.session.commit()
#     assert_sql_result(sql, [], "popped")
